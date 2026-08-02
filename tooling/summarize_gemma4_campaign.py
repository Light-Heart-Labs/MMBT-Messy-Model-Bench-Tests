#!/usr/bin/env python3
"""Generate compact raw N=3/N=10 Gemma scorecards from immutable run evidence."""
from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


TASKS = [
    "p1_bugfix", "p1_testwrite", "p1_refactor", "p2_extract", "p2_ci",
    "p2_hallucination", "p2_triage", "p3_doc", "p3_business",
    "p3_market", "p3_writing", "p3_pm",
]
PASS_VERDICTS = {"PASS", "STRUCTURAL_PASS"}


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def median(values):
    return round(statistics.median(values), 3) if values else None


def finish_reason(record: dict) -> str:
    summary = record.get("summary") or {}
    if summary.get("finish_reason"):
        return summary["finish_reason"]
    if record.get("terminal_label"):
        return f"terminal:{record['terminal_label']}"
    return "MISSING"


def quality_outcome(record: dict) -> str:
    if record.get("verdict"):
        return record["verdict"]
    if record.get("terminal_label"):
        return f"TERMINAL:{record['terminal_label']}"
    return "MISSING"


def aggregate_records(records: list[dict]) -> dict:
    completed = [
        record for record in records
        if record.get("summary") or record.get("terminal_label")
    ]
    normal_completed = [record for record in records if record.get("summary")]
    terminal = [record for record in records if record.get("terminal_label")]
    graded = [record for record in records if record.get("verdict")]
    scored = [record for record in records if record.get("verdict") or record.get("terminal_label")]
    telemetry = [record["telemetry"] for record in records if record.get("telemetry")]
    per_task = {}
    for task in TASKS:
        task_records = [record for record in records if record["task"] == task]
        verdicts = Counter(record.get("verdict") or "MISSING" for record in task_records)
        outcomes = Counter(quality_outcome(record) for record in task_records)
        finishes = Counter(finish_reason(record) for record in task_records)
        per_task[task] = {
            "runs": len(task_records),
            "graded": sum(record.get("verdict") is not None for record in task_records),
            "scored_outcomes": sum(
                record.get("verdict") is not None or record.get("terminal_label") is not None
                for record in task_records
            ),
            "raw_passes": sum(record.get("verdict") in PASS_VERDICTS for record in task_records),
            "verdicts": dict(sorted(verdicts.items())),
            "quality_outcomes": dict(sorted(outcomes.items())),
            "finish_reasons": dict(sorted(finishes.items())),
        }
    model_tps = [
        record["cost"]["throughput"]["completion_tps_avg"]
        for record in records
        if isinstance((((record.get("cost") or {}).get("throughput") or {}).get("completion_tps_avg")), (int, float))
    ]
    wall_s = []
    completion_tokens = []
    for record in completed:
        cost = record.get("cost") or {}
        summary = record.get("summary") or {}
        wall = cost.get("wall_s", summary.get("elapsed_s"))
        tokens = (cost.get("tokens") or {}).get(
            "completion_total", summary.get("total_completion_tokens")
        )
        if isinstance(wall, (int, float)):
            wall_s.append(wall)
        if isinstance(tokens, (int, float)):
            completion_tokens.append(tokens)
    return {
        "runs": len(records),
        "completed": len(completed),
        "normal_completed": len(normal_completed),
        "terminal_outcomes": len(terminal),
        "graded": len(graded),
        "scored_outcomes": len(scored),
        "raw_passes": sum(record.get("verdict") in PASS_VERDICTS for record in records),
        "raw_pass_rate": (
            round(sum(record.get("verdict") in PASS_VERDICTS for record in records) / len(scored), 6)
            if scored else None
        ),
        "verdicts": dict(sorted(Counter(record.get("verdict") or "MISSING" for record in records).items())),
        "quality_outcomes": dict(sorted(Counter(quality_outcome(record) for record in records).items())),
        "finish_reasons": dict(sorted(Counter(finish_reason(record) for record in records).items())),
        "wall_s": {"sum": round(sum(wall_s), 3), "median": median(wall_s), "max": max(wall_s) if wall_s else None},
        "completion_tokens": {
            "sum": sum(completion_tokens), "median": median(completion_tokens),
            "max": max(completion_tokens) if completion_tokens else None,
        },
        "model_call_completion_tps": {"median": median(model_tps), "min": min(model_tps) if model_tps else None,
                                      "max": max(model_tps) if model_tps else None},
        "telemetry": {
            "runs": len(telemetry),
            "coverage_mean": round(sum(row["coverage"] for row in telemetry) / len(telemetry), 6) if telemetry else None,
            "active_gpu_mean_power_w_mean": round(sum(row["mean_power_w"] for row in telemetry) / len(telemetry), 3) if telemetry else None,
            "active_gpu_mean_sm_util_pct_mean": round(sum(row["mean_sm_util_pct"] for row in telemetry) / len(telemetry), 3) if telemetry else None,
            "max_temp_c": max((row["max_temp_c"] for row in telemetry), default=None),
        },
        "per_task": per_task,
    }


def markdown(document: dict) -> str:
    aggregate = document["aggregate"]
    target_n = document["target_n"]
    lines = [
        f"# Gemma 4 31B Q4 raw canonical scorecard (N={target_n})",
        "",
        "> Raw grader verdicts only. Any reproducible correction is a separate overlay tied to unchanged archive and grader hashes.",
        "",
        f"- Evidence-complete runs: {aggregate['completed']}/{aggregate['runs']}",
        f"- Normal completed workspaces: {aggregate['normal_completed']}/{aggregate['runs']}",
        f"- Explicit terminal outcomes: {aggregate['terminal_outcomes']}/{aggregate['runs']}",
        f"- Graded runs: {aggregate['graded']}/{aggregate['runs']}",
        f"- Raw pass-equivalent outcomes: {aggregate['raw_passes']}/{aggregate['scored_outcomes']}",
        f"- Median model-call completion throughput: {aggregate['model_call_completion_tps']['median']} tok/s",
        f"- Median cell wall time: {aggregate['wall_s']['median']} s",
        f"- Telemetry-complete runs: {aggregate['telemetry']['runs']}/{aggregate['runs']}",
        "",
        "| Task | Raw pass | Scored | Finish reasons | Quality outcomes |",
        "|---|---:|---:|---|---|",
    ]
    for task in TASKS:
        row = aggregate["per_task"][task]
        finishes = ", ".join(f"{key}:{value}" for key, value in row["finish_reasons"].items())
        outcomes = ", ".join(f"{key}:{value}" for key, value in row["quality_outcomes"].items())
        lines.append(f"| `{task}` | {row['raw_passes']}/{row['scored_outcomes']} | {row['scored_outcomes']}/{row['runs']} | {finishes} | {outcomes} |")
    lines += [
        "",
        "## Methodology boundary",
        "",
        "A `done_signal` is a finish behavior, not a pass. `PASS` and `STRUCTURAL_PASS` count only as raw pass-equivalent grader verdicts. A preserved terminal label is reported as a distinct non-pass quality outcome, never fabricated into a normal grader verdict. Model-call throughput excludes tool execution; wall time includes it. Telemetry is per attributed replica GPU, while CPU package power is shared host context and AC wall power is unavailable to software.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--label", default="gemma4-31b-q4")
    parser.add_argument("--target-n", type=int, required=True)
    parser.add_argument("--allow-pretelemetry-run", action="append", default=[])
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-markdown", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    allowed = set(args.allow_pretelemetry_run)
    records = []
    errors = []
    for task in TASKS:
        for rep in range(1, args.target_n + 1):
            name = f"{task}_{args.label}_v{rep}"
            run = root / "logs" / name
            summary = read_json(run / "summary.json")
            grade = read_json(run / "grade.json")
            cost = read_json(run / "cost.json")
            label_doc = read_json(run / "label.json")
            terminal_label = (
                label_doc.get("primary")
                if summary is None and isinstance(label_doc, dict) else None
            )
            telemetry_raw = read_json(run / "gpu_telemetry.json")
            if summary is None and not terminal_label:
                errors.append(f"{name}: missing summary.json or explicit terminal label")
            if grade is None and not terminal_label:
                errors.append(f"{name}: missing grade.json")
            if cost is None:
                errors.append(f"{name}: missing cost.json")
            if telemetry_raw is None and (name not in allowed or terminal_label):
                errors.append(f"{name}: missing gpu_telemetry.json")
            telemetry = None
            if telemetry_raw:
                telemetry = {
                    "coverage": telemetry_raw["sampling"]["coverage_fraction_of_wall"],
                    "mean_power_w": telemetry_raw["active_gpu"]["mean_power_w"],
                    "mean_sm_util_pct": telemetry_raw["active_gpu"]["mean_sm_util_pct"],
                    "max_temp_c": telemetry_raw["active_gpu"]["max_temp_c"],
                }
            records.append({
                "run_name": name, "task": task, "replicate": rep,
                "summary": summary, "verdict": grade.get("verdict") if grade else None,
                "terminal_label": terminal_label, "label": label_doc,
                "cost": cost, "telemetry": telemetry,
            })
    document = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "label": args.label,
        "target_n": args.target_n,
        "passed": not errors,
        "errors": errors,
        "aggregate": aggregate_records(records),
        "runs": records,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(document, indent=2) + "\n")
    args.output_markdown.write_text(markdown(document))
    print(json.dumps({
        "passed": document["passed"], "runs": len(records),
        "raw_passes": document["aggregate"]["raw_passes"], "errors": len(errors),
    }, sort_keys=True))
    raise SystemExit(0 if document["passed"] else 1)


if __name__ == "__main__":
    main()
