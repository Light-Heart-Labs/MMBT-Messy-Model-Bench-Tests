#!/usr/bin/env python3
"""Per-cell supervisor for the corrective crossover campaign.

Runs exactly ONE cell (family x seed x model x arm) through the existing
``tooling/scripts/run_microbench.sh`` -> ``tooling/harness.py`` path, with:

  * arm sampler + seed passed through the verified BENCH_* env plumbing
    (BENCH_SEED -> --seed -> request body "seed"; verified firsthand);
  * a live loop terminator thread (PREREGISTRATION section 4b): exact
    consecutive run >= threshold over (tool_name, canonical_json(args)) ->
    mechanical harness kill + label.json {"primary": "loop-run30", ...};
  * the preregistered wall-clock ceiling (section 4c, default 3 h) ->
    mechanical kill + label.json {"primary": "timeout", ...} (only when the
    cell has at least one model turn; a zero-turn 3 h cell is an infra
    failure, not a model outcome);
  * mechanical infra classification (delivery_validator) with quarantine +
    same-seed rerun, machine-logged to logs/corrective/rerun_ledger.jsonl.
    Fixed N: reruns replace quarantined infra failures only; terminal
    outcomes are never rerun and never judged by an operator.

stdlib only. Invoked by run_crossover.sh; usable standalone for one cell.
"""

import argparse
import datetime
import fcntl
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import delivery_validator  # noqa: E402
import loop_terminator  # noqa: E402

TOOLING = HERE.parent
REPO_ROOT = TOOLING.parent
LOGS = REPO_ROOT / "logs"
CORRECTIVE_LOGS = LOGS / "corrective"
LEDGER = CORRECTIVE_LOGS / "rerun_ledger.jsonl"
OUTCOMES = CORRECTIVE_LOGS / "cell_outcomes.jsonl"


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_jsonl(path, obj):
    """Locked append so two concurrent supervisors never interleave lines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(obj, sort_keys=True) + "\n")
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)


def phase_for_seed(cfg, seed):
    for phase, plan in cfg["host_plan"].items():
        if seed in plan["seeds"]:
            return phase, plan
    raise SystemExit(f"seed {seed} not in any host_plan phase")


def build_env(cfg, model, seed, family):
    env = dict(os.environ)
    s = cfg["sampler"]
    env["BENCH_TEMP"] = str(s["benchmark_temperature"])
    env["BENCH_TOP_P"] = str(s["benchmark_top_p"])
    env["BENCH_TOP_K"] = str(s["benchmark_top_k"])
    env["BENCH_MIN_P"] = str(s["benchmark_min_p"])
    env["BENCH_PRESENCE_PENALTY"] = str(s["benchmark_presence_penalty"])
    env["BENCH_REPEAT_PENALTY"] = str(s["benchmark_repeat_penalty"])
    env["BENCH_SEED"] = str(seed)
    env["BENCH_TASK_ONLY"] = family
    env["BENCH_SANDBOX_GPUS"] = str(cfg.get("benchmark_sandbox_gpus", "none"))
    env["BENCH_MAX_OUTPUT_TOKENS_CAP"] = str(cfg.get("benchmark_max_output_tokens_cap", 262144))
    if model.get("preserve_thinking") is not None:
        env["BENCH_PRESERVE_THINKING"] = "true" if model["preserve_thinking"] else "false"
    else:
        env.pop("BENCH_PRESERVE_THINKING", None)
    if model.get("reasoning_effort_location"):
        env["BENCH_REASONING_EFFORT_LOCATION"] = model["reasoning_effort_location"]
    else:
        env.pop("BENCH_REASONING_EFFORT_LOCATION", None)
    if cfg.get("serving_manifest"):
        env["BENCH_SERVING_MANIFEST"] = cfg["serving_manifest"]
    return env


def transcript_has_model_turn(transcript):
    n = delivery_validator.transcript_model_events(transcript)
    return bool(n)


def write_timeout_label(run_dir, ceiling_secs, harness_pid, kill_result):
    label_path = run_dir / "label.json"
    if label_path.exists():
        return False
    label = {
        "primary": "timeout",
        "metric": "wall_clock_secs",
        "value": ceiling_secs,
        "automated": True,
        "written_at": now_iso(),
        "written_by": "tooling/corrective/cell_supervisor.py",
        "harness_pid": harness_pid,
        "kill": kill_result,
    }
    tmp = label_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(label, indent=2) + "\n")
    tmp.rename(label_path)
    return True


def kill_harness(run_name, grace_secs=30):
    pid = loop_terminator.find_harness_pid(run_name)
    if pid is None:
        return None, "harness-pid-not-found"
    return pid, loop_terminator.terminate_pid(pid, grace_secs)


def cleanup_sandbox(run_name):
    subprocess.run(["docker", "rm", "-f", f"bench-sandbox-{run_name}"],
                   capture_output=True)


def quarantine(run_dir, attempt):
    qdir = CORRECTIVE_LOGS / "quarantine"
    qdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = qdir / f"{run_dir.name}.attempt{attempt}.{stamp}"
    shutil.move(str(run_dir), str(dest))
    return dest


def already_terminal(run_dir):
    """True when the cell already holds terminal evidence (idempotent resume)."""
    if (run_dir / "summary.json").exists() and (run_dir / "workspace_final.tar.gz").exists():
        return True
    label, _ = delivery_validator.load_json(run_dir / "label.json")
    return bool(label) and label.get("primary") in ("loop-run30", "identical-call-loop", "timeout")


def run_cell(cfg, model_key, family, seed, max_infra_retries, dry_run=False):
    phase, plan = phase_for_seed(cfg, seed)
    model = cfg["models"][model_key]
    port = plan[model_key]["port"]
    label = f"{model['label']}-s{seed}"
    run_name = f"{family}_{label}_v1"
    run_dir = LOGS / run_name
    ceiling = int(cfg.get("wall_clock_ceiling_secs", 10800))
    threshold = int(cfg.get("loop_threshold", 30))
    effort = model.get("reasoning_effort") or ""
    thinking = cfg["thinking"]
    maxlen = str(cfg.get("max_model_len", 262144))

    plan_row = {
        "run_name": run_name, "arm": cfg["arm"], "family": family, "seed": seed,
        "model_key": model_key, "model": model["alias"], "phase": phase,
        "tower": plan[model_key]["tower"], "port": port, "label": label,
        "thinking": thinking, "reasoning_effort": effort or None,
        "ceiling_secs": ceiling, "loop_threshold": threshold,
    }
    if dry_run:
        print(json.dumps({"dry_run": True, **plan_row}))
        return 0

    argv = ["bash", str(TOOLING / "scripts" / "run_microbench.sh"),
            model["alias"], str(port), label, "1", effort, thinking, maxlen]

    attempt = 0
    while True:
        attempt += 1
        if run_dir.is_dir() and already_terminal(run_dir):
            validation = delivery_validator.validate_cell(
                run_dir, family=family,
                artifacts_spec=delivery_validator.load_artifacts_config(
                    str(HERE / "configs" / "family_artifacts.json")))
            if validation["classification"] != "infra":
                outcome = {"t": now_iso(), "attempt": attempt, "resumed": True,
                           **plan_row, **{k: validation[k] for k in
                                          ("delivery", "classification", "reasons",
                                           "finish_reason", "label_primary")}}
                append_jsonl(OUTCOMES, outcome)
                print(json.dumps(outcome))
                return 0
            # A resumed cell that LOOKS complete but classifies as infra
            # (e.g. api_error finish with summary+tarball written) is
            # quarantined + rerun like any other infra failure.
            qpath = quarantine(run_dir, attempt)
            append_jsonl(LEDGER, {
                "t": now_iso(), "run_name": run_name, "arm": cfg["arm"],
                "family": family, "seed": seed, "model_key": model_key,
                "model": model["alias"], "phase": phase, "attempt": attempt,
                "classification": "infra", "resumed": True,
                "reasons": validation["reasons"],
                "quarantine_path": str(qpath),
                "action": "quarantine+same-seed-rerun",
            })

        CORRECTIVE_LOGS.mkdir(parents=True, exist_ok=True)
        cell_log = CORRECTIVE_LOGS / "cell-logs" / f"{run_name}.attempt{attempt}.log"
        cell_log.parent.mkdir(parents=True, exist_ok=True)

        stop = threading.Event()
        watch_result = {}

        def watcher():
            watch_result.update(loop_terminator.watch(
                run_dir / "transcript.jsonl", run_name,
                threshold=threshold, grace_secs=30, poll_secs=2.0,
                stop_event=stop))

        with open(cell_log, "a") as lf:
            lf.write(f"# {now_iso()} attempt {attempt} argv={argv}\n")
            lf.flush()
            proc = subprocess.Popen(
                argv, stdout=lf, stderr=subprocess.STDOUT,
                env=build_env(cfg, model, seed, family),
                cwd=str(REPO_ROOT), start_new_session=True)
            wt = threading.Thread(target=watcher, daemon=True)
            wt.start()
            timed_out = False
            try:
                proc.wait(timeout=ceiling)
            except subprocess.TimeoutExpired:
                timed_out = True
                pid, kill_result = kill_harness(run_name)
                if transcript_has_model_turn(run_dir / "transcript.jsonl"):
                    write_timeout_label(run_dir, ceiling, pid, kill_result)
                # else: leave unlabeled -> validator classifies infra
                try:
                    proc.wait(timeout=120)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            stop.set()
            wt.join(timeout=60)

        cleanup_sandbox(run_name)

        validation = delivery_validator.validate_cell(
            run_dir, family=family,
            artifacts_spec=delivery_validator.load_artifacts_config(
                str(HERE / "configs" / "family_artifacts.json")))
        outcome = {"t": now_iso(), "attempt": attempt, "timed_out": timed_out,
                   "loop_watch": {k: watch_result.get(k) for k in
                                  ("fired", "longest_run", "total_tool_calls")},
                   **plan_row,
                   **{k: validation[k] for k in
                      ("delivery", "classification", "reasons",
                       "finish_reason", "label_primary")}}

        if validation["classification"] != "infra":
            append_jsonl(OUTCOMES, outcome)
            print(json.dumps(outcome))
            return 0

        # ----- infra failure: mechanical quarantine + same-seed rerun -----
        qpath = quarantine(run_dir, attempt) if run_dir.is_dir() else None
        ledger_entry = {
            "t": now_iso(), "run_name": run_name, "arm": cfg["arm"],
            "family": family, "seed": seed, "model_key": model_key,
            "model": model["alias"], "phase": phase, "attempt": attempt,
            "classification": "infra", "reasons": validation["reasons"],
            "quarantine_path": str(qpath) if qpath else None,
            "action": ("quarantine+same-seed-rerun"
                       if attempt <= max_infra_retries else
                       "quarantine+exhausted-STOP"),
        }
        append_jsonl(LEDGER, ledger_entry)
        print(json.dumps(ledger_entry))
        if attempt > max_infra_retries:
            append_jsonl(OUTCOMES, {**outcome, "classification": "infra-exhausted"})
            return 4


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, help="arm config json")
    ap.add_argument("--model-key", required=True, help="q38 | q36")
    ap.add_argument("--family", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--max-infra-retries", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)
    if args.family not in cfg["families"]:
        raise SystemExit(f"family {args.family!r} not in arm {cfg['arm']}")
    if args.seed not in cfg["seeds"]:
        raise SystemExit(f"seed {args.seed} not in arm {cfg['arm']} (fixed-N: no extra seeds)")
    if args.model_key not in cfg["models"]:
        raise SystemExit(f"model key {args.model_key!r} not in arm {cfg['arm']}")

    return run_cell(cfg, args.model_key, args.family, args.seed,
                    args.max_infra_retries, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
