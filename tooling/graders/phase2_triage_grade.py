#!/usr/bin/env python3
"""Triage grader: compares the agent's triage_results.json against the
ground-truth labels and emits accuracy + duplicate-detection metrics.

Usage:
    phase2_triage_grade.py <workspace_dir> <ground_truth_path> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def grade(workspace: Path, ground_truth_path: Path) -> dict:
    triage_path = workspace / "triage_results.json"
    if not triage_path.exists():
        return {
            "task": "triage",
            "verdict": "MISSING_OUTPUT",
            "notes": f"agent did not produce {triage_path}",
        }
    try:
        agent = json.loads(triage_path.read_text())
    except json.JSONDecodeError as e:
        return {"task": "triage", "verdict": "INVALID_JSON", "notes": str(e)}
    gt = json.loads(ground_truth_path.read_text())

    agent_tickets = agent.get("tickets", {})
    gt_tickets = gt.get("tickets", {})

    # Per-ticket accuracy
    correct_category = 0
    correct_urgency = 0
    category_errors = []
    urgency_errors = []
    missing_tickets = []

    for tid, gt_label in gt_tickets.items():
        if tid not in agent_tickets:
            missing_tickets.append(tid)
            continue
        a = agent_tickets[tid]
        gt_cat = gt_label["category"]
        gt_urg = gt_label["urgency"]
        a_cat = a.get("category")
        a_urg = a.get("urgency")
        if a_cat == gt_cat:
            correct_category += 1
        else:
            category_errors.append({"id": tid, "predicted": a_cat, "actual": gt_cat})
        if a_urg == gt_urg:
            correct_urgency += 1
        else:
            urgency_errors.append({"id": tid, "predicted": a_urg, "actual": gt_urg})

    n = len(gt_tickets)
    cat_accuracy = round(correct_category / n, 3) if n else None
    urg_accuracy = round(correct_urgency / n, 3) if n else None

    # Duplicate-cluster detection
    gt_clusters = [tuple(sorted(c)) for c in gt.get("summary", {}).get("duplicate_clusters", [])]
    agent_clusters_raw = (agent.get("summary") or {}).get("duplicate_clusters") or []
    agent_clusters = [tuple(sorted(c)) for c in agent_clusters_raw]

    dup_correct = sum(1 for c in gt_clusters if c in agent_clusters)
    dup_extra = [list(c) for c in agent_clusters if c not in gt_clusters]
    dup_missed = [list(c) for c in gt_clusters if c not in agent_clusters]

    # Pass criteria
    cat_threshold = 0.80  # 80% category accuracy
    urg_threshold = 0.70  # 70% urgency accuracy (more subjective)
    dup_threshold = 0.50  # at least half of duplicate clusters caught (only 2 in this set)
    dup_recall = dup_correct / max(len(gt_clusters), 1)

    verdict = (
        "PASS" if (
            (cat_accuracy or 0) >= cat_threshold
            and (urg_accuracy or 0) >= urg_threshold
            and dup_recall >= dup_threshold
            and len(missing_tickets) == 0
        )
        else "FAIL"
    )

    return {
        "task": "triage",
        "verdict": verdict,
        "scores": {
            "category_accuracy": cat_accuracy,
            "urgency_accuracy": urg_accuracy,
            "duplicate_recall": round(dup_recall, 3),
            "duplicate_clusters_correct": dup_correct,
            "duplicate_clusters_total": len(gt_clusters),
            "fabricated_clusters": len(dup_extra),
        },
        "thresholds": {
            "category_accuracy": cat_threshold,
            "urgency_accuracy": urg_threshold,
            "duplicate_recall": dup_threshold,
        },
        "errors": {
            "missing_tickets": missing_tickets,
            "category_errors": category_errors,
            "urgency_errors": urgency_errors,
            "fabricated_clusters": dup_extra,
            "missed_clusters": dup_missed,
        },
        "summary_self_consistency": {
            "agent_summary_present": "summary" in agent,
            "summary_by_category": (agent.get("summary") or {}).get("by_category"),
        },
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
