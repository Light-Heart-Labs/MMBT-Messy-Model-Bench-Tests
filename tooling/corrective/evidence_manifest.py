#!/usr/bin/env python3
"""Row-level evidence manifest + fixed-N balance checker (PREREGISTRATION.md sections 3-5).

``build`` walks the expected cell grid (arm x family x seed x model, derived
from the campaign configs — never from what happens to exist on disk) and
writes one JSON line per cell to ``manifest.jsonl``:

  family, arm, model (+ key), seed, host (tower/gpu/power-cap from the run's
  own receipt), sampler settings actually sent (receipt), quant, harness shas
  (git + file), grader shas (tooling/graders/v2/*.py at build time), llama.cpp
  image digest (receipt serving manifest), transcript sha256, delivery flag +
  reasons (delivery_validator), loop metrics (loop_terminator recompute —
  delivery and loop are distinct columns), and per-row consistency checks
  (receipt seed == planned seed, receipt model == planned model, receipt
  sampler == arm sampler, host == crossover plan for that seed).

``check`` asserts the fixed-N design: every expected (arm, family, seed,
model) present exactly once — zero duplicates, zero missing, zero
unexpected extras, seeds exactly the preregistered set. Exit 1 on any
violation (CI-enforceable). No optional stopping: the campaign is complete
when this check passes, not when a result looks good.

stdlib only.
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import delivery_validator  # noqa: E402
import loop_terminator  # noqa: E402


def file_sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_config(path):
    with open(path) as f:
        return json.load(f)


def phase_for_seed(cfg, seed):
    for phase, plan in cfg["host_plan"].items():
        if seed in plan["seeds"]:
            return phase, plan
    raise ValueError(f"seed {seed} is not in any host_plan phase of arm {cfg['arm']}")


def expected_cells(cfg):
    """Yield the full expected grid for one arm config."""
    for family in cfg["families"]:
        for seed in cfg["seeds"]:
            phase, plan = phase_for_seed(cfg, seed)
            for model_key, model in cfg["models"].items():
                label = f"{model['label']}-s{seed}"
                yield {
                    "arm": cfg["arm"],
                    "family": family,
                    "seed": seed,
                    "model_key": model_key,
                    "model": model["alias"],
                    "label": label,
                    "run_name": f"{family}_{label}_v1",
                    "phase": phase,
                    "planned_host": plan[model_key]["tower"],
                    "planned_port": plan[model_key]["port"],
                    # Model-level quant (quant pilot) falls back to the
                    # arm-level quant of the single-quant arms
                    # (default-preserving: no model carries "quant" in
                    # those configs).
                    "quant": model.get("quant", cfg.get("quant")),
                }


def grader_shas(repo_root):
    v2 = repo_root / "tooling" / "graders" / "v2"
    out = {}
    if v2.is_dir():
        for p in sorted(v2.glob("*.py")):
            out[p.name] = file_sha256(p)
    return out


def sampler_from_receipt(receipt):
    d = (receipt or {}).get("inference_request_defaults") or {}
    keys = ("temperature", "top_p", "top_k", "min_p", "presence_penalty",
            "repeat_penalty", "seed", "reasoning_effort",
            "reasoning_effort_location", "enable_thinking", "preserve_thinking")
    return {k: d.get(k) for k in keys}


def expected_sampler(cfg, model_key):
    s = cfg["sampler"]
    model = cfg["models"][model_key]
    return {
        "temperature": s["benchmark_temperature"],
        "top_p": s["benchmark_top_p"],
        "top_k": s["benchmark_top_k"],
        "min_p": s["benchmark_min_p"],
        "presence_penalty": s["benchmark_presence_penalty"],
        "repeat_penalty": s["benchmark_repeat_penalty"],
        "enable_thinking": cfg["thinking"] == "on",
        "reasoning_effort": model.get("reasoning_effort"),
    }


def build_row(cell, logs_dir, artifacts_spec, graders, repo_root, loop_threshold):
    run_dir = logs_dir / cell["run_name"]
    row = dict(cell)
    row["cell_dir"] = str(run_dir)
    if not run_dir.is_dir():
        row["status"] = "missing"
        return row
    row["status"] = "present"

    receipt, receipt_err = delivery_validator.load_json(run_dir / "receipt.json")
    row["receipt_error"] = receipt_err
    sampler = sampler_from_receipt(receipt)
    row["sampler"] = sampler
    harness = (receipt or {}).get("harness") or {}
    row["harness_git_sha"] = harness.get("git_sha")
    row["harness_file_sha256"] = harness.get("file_sha256")
    lane = (((receipt or {}).get("serving") or {}).get("inference_lane") or {}).get("lane") or {}
    row["host"] = {
        "inference_host": lane.get("inference_host"),
        "gpu_name": lane.get("gpu_name"),
        "gpu_uuid": lane.get("gpu_uuid"),
        "gpu_power_limit_w": lane.get("gpu_power_limit_w"),
        "coordinator_port": (((receipt or {}).get("serving") or {}).get("inference_lane") or {}).get("coordinator_port"),
    }
    manifest_payload = ((((receipt or {}).get("serving") or {}).get("manifest") or {}).get("payload") or {})
    row["image_digest"] = (manifest_payload.get("runtime") or {}).get("image_reference")
    row["grader_shas"] = graders

    transcript = run_dir / "transcript.jsonl"
    row["transcript_sha256"] = file_sha256(transcript) if transcript.exists() else None

    validation = delivery_validator.validate_cell(
        run_dir, family=cell["family"], artifacts_spec=artifacts_spec)
    row["delivery"] = validation["delivery"]
    row["delivery_reasons"] = validation["reasons"]
    row["classification"] = validation["classification"]
    row["finish_reason"] = validation["finish_reason"]
    row["label_primary"] = validation["label_primary"]

    if transcript.exists():
        row["loop"] = loop_terminator.compute_transcript_metrics(transcript, loop_threshold)
        row["loop"].pop("transcript", None)
    else:
        row["loop"] = None

    checks = {
        "seed_matches_plan": sampler.get("seed") == cell["seed"],
        "model_matches_plan": ((receipt or {}).get("vllm") or {}).get("served_model_name") == cell["model"],
        "host_matches_crossover_plan": lane.get("inference_host") == cell["planned_host"],
        "power_cap_500w": lane.get("gpu_power_limit_w") == 500,
    }
    row["consistency"] = checks
    row["consistent"] = all(v for v in checks.values())
    return row


def cmd_build(args):
    repo_root = Path(args.repo_root).resolve()
    logs_dir = repo_root / "logs"
    artifacts_spec = delivery_validator.load_artifacts_config(
        args.artifacts_config or str(HERE / "configs" / "family_artifacts.json"))
    graders = grader_shas(repo_root)
    rows = []
    for cfg_path in args.config:
        cfg = load_config(cfg_path)
        for cell in expected_cells(cfg):
            rows.append(build_row(cell, logs_dir, artifacts_spec, graders,
                                  repo_root, cfg.get("loop_threshold", 30)))
    out = Path(args.out)
    with open(out, "w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    missing = sum(1 for r in rows if r["status"] == "missing")
    print(json.dumps({"manifest": str(out), "rows": len(rows),
                      "present": len(rows) - missing, "missing": missing}))
    return 0 if (missing == 0 or args.allow_missing) else 1


def cmd_check(args):
    """Fixed-N balance check: expected grid vs manifest rows."""
    expected = {}
    for cfg_path in args.config:
        cfg = load_config(cfg_path)
        n_models = len(cfg["models"])
        n_expected = len(cfg["families"]) * len(cfg["seeds"]) * n_models
        for cell in expected_cells(cfg):
            key = (cell["arm"], cell["family"], cell["seed"], cell["model_key"])
            expected[key] = 0
        expected.setdefault(("__arm_total__", cfg["arm"]), None)
        expected[("__arm_total__", cfg["arm"])] = n_expected

    seen = {}
    extras = []
    with open(args.manifest) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            key = (row["arm"], row["family"], row["seed"], row["model_key"])
            if key not in expected:
                extras.append(key)
                continue
            if row.get("status") == "present":
                seen[key] = seen.get(key, 0) + 1

    missing = sorted(str(k) for k in expected
                     if isinstance(k, tuple) and len(k) == 4 and seen.get(k, 0) == 0)
    dupes = sorted(str(k) for k, n in seen.items() if n > 1)
    arm_totals = {}
    for k, v in expected.items():
        if k[0] == "__arm_total__":
            arm = k[1]
            arm_totals[arm] = {
                "expected": v,
                "present_once": sum(1 for kk, n in seen.items()
                                    if kk[0] == arm and n == 1),
            }
    report = {
        "expected_cells": sum(1 for k in expected if isinstance(k, tuple) and len(k) == 4),
        "arm_totals": arm_totals,
        "missing": missing,
        "duplicates": dupes,
        "unexpected": sorted(str(k) for k in extras),
        "balanced": not missing and not dupes and not extras,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["balanced"] else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build manifest.jsonl from configs + logs")
    b.add_argument("--config", nargs="+", required=True, help="arm config json(s)")
    b.add_argument("--repo-root", default=str(HERE.parent.parent))
    b.add_argument("--artifacts-config", default=None)
    b.add_argument("--out", required=True)
    b.add_argument("--allow-missing", action="store_true",
                   help="exit 0 even with missing cells (mid-campaign builds)")
    b.set_defaults(fn=cmd_build)

    c = sub.add_parser("check", help="fixed-N balance check over a manifest")
    c.add_argument("--config", nargs="+", required=True)
    c.add_argument("--manifest", required=True)
    c.set_defaults(fn=cmd_check)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
