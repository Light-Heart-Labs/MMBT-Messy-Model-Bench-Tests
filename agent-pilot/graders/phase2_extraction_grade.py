#!/usr/bin/env python3
"""Structured-extraction grader: matches agent's extraction_results.json against
the planted ground_truth.json field-by-field. Numeric tolerance per field.

Usage:
    phase2_extraction_grade.py <workspace_dir> <ground_truth_path> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def normalize_string(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def num_match(a, b, tolerance_pct: float) -> bool:
    """True if a is within tolerance_pct of b."""
    if a is None or b is None:
        return False
    try:
        a = float(a); b = float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) / abs(b) * 100 <= tolerance_pct


def grade_field(name: str, gt: dict, agent_value):
    """Returns (verdict, why) for one field. verdict is 'correct', 'wrong', 'missing', 'fabricated'."""
    if agent_value is None:
        return ("missing", "agent emitted null or omitted the field")
    typ = gt["type"]
    answer = gt["answer"]
    if typ in ("number", "integer"):
        tol = gt.get("tolerance_pct", 0.5)
        if num_match(agent_value, answer, tol):
            return ("correct", None)
        return ("wrong", f"expected ~{answer} (±{tol}%), got {agent_value}")
    if typ == "string":
        mode = gt.get("match_mode", "exact")
        a = str(agent_value)
        if mode == "exact":
            if a == str(answer):
                return ("correct", None)
        elif mode == "case_insensitive_substring":
            if normalize_string(answer) in normalize_string(a) or normalize_string(a) in normalize_string(answer):
                return ("correct", None)
        return ("wrong", f"expected ~{answer!r}, got {a!r}")
    if typ == "date":
        a = str(agent_value)
        # Accept "YYYY-MM-DD" or "Month DD, YYYY" forms
        from datetime import datetime
        for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%B %-d, %Y"):
            try:
                dt = datetime.strptime(a, fmt)
                if dt.strftime("%Y-%m-%d") == answer:
                    return ("correct", None)
            except ValueError:
                continue
        return ("wrong", f"expected {answer}, got {a!r}")
    return ("wrong", f"unknown type {typ}")


def grade(workspace: Path, gt_path: Path) -> dict:
    out_path = workspace / "extraction_results.json"
    if not out_path.exists():
        return {"task": "extraction", "verdict": "MISSING_OUTPUT",
                "notes": f"agent did not produce {out_path}"}
    try:
        agent = json.loads(out_path.read_text())
    except json.JSONDecodeError as e:
        return {"task": "extraction", "verdict": "INVALID_JSON", "notes": str(e)}
    gt = json.loads(gt_path.read_text())

    agent_fields = agent.get("fields", {})
    agent_uncertain = set(agent.get("uncertain", []) or [])
    field_results = {}
    counts = {"correct": 0, "wrong": 0, "missing": 0}
    for name, gt_field in gt["fields"].items():
        if name not in agent_fields:
            field_results[name] = {"verdict": "missing", "why": "field key absent from output"}
            counts["missing"] += 1
            continue
        verdict, why = grade_field(name, gt_field, agent_fields.get(name))
        field_results[name] = {"verdict": verdict, "why": why,
                                "agent_value": agent_fields.get(name),
                                "expected": gt_field["answer"]}
        if verdict in counts:
            counts[verdict] += 1

    n = len(gt["fields"])
    accuracy = round(counts["correct"] / n, 3)
    # Pass criteria: 80% correct AND no fabricated answers (agent fields not in schema)
    extra_fields = [k for k in agent_fields if k not in gt["fields"]]
    pass_threshold = 0.80
    overall = (
        "PASS" if (accuracy >= pass_threshold and len(extra_fields) == 0)
        else "FAIL"
    )
    return {
        "task": "extraction",
        "verdict": overall,
        "scores": {
            "accuracy": accuracy,
            "correct": counts["correct"],
            "wrong": counts["wrong"],
            "missing": counts["missing"],
            "extra_fields": len(extra_fields),
        },
        "thresholds": {"accuracy": pass_threshold},
        "field_results": field_results,
        "extra_fields": extra_fields,
        "agent_uncertain": list(agent_uncertain),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("ground_truth")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = grade(Path(args.workspace), Path(args.ground_truth))
    out_path = Path(args.out) if args.out else (Path(args.workspace) / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
