#!/usr/bin/env python3
r"""Triage grader, v2.

Provenance: copied from tooling/graders/phase2_triage_grade.py
(v1, sha256 ea3eebcf6a2fc085276e555f2cb1a54239e1dc9286bac3cb2300f01929b855a1).

Changes vs v1 (defect D3, PREREGISTRATION.md section 8 / grader-defects.md):

- The urgency vocabulary is parsed from the v2 task brief
  (tooling/tasks/v2/task_triage.md, "## Urgency" section) instead of being
  implicit in whatever labels the ground truth happens to use.  Both the
  ground truth and the agent output are validated against it: an
  out-of-vocabulary ground-truth label aborts grading (fixture defect); an
  out-of-vocabulary agent label is an urgency error and is reported in
  ``errors.invalid_urgency_labels``.

- This grader is designed to run against the v2 ground truth
  (tooling/graders/v2/ground_truth/phase2_triage.json), which aligns the
  labels to the brief: ``n/a`` is credited for the three spam-or-noise
  tickets 004/009/021 (the brief defines ``n/a`` as "for noise/spam where
  urgency doesn't apply"), and ticket 029 (extortion) is resolved
  consistently with the brief's rules-of-the-road as spam-or-noise / n/a.
  See tooling/graders/v2/CHANGES.md for the documented resolution.

Comparison logic, duplicate-cluster scoring, thresholds and output shape are
otherwise unchanged from v1.

Usage:
    phase2_triage_grade.py <workspace_dir> <ground_truth_path> [--brief task_brief.md] [--out grade.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# Default v2 brief, resolved relative to the repository root
# (this file lives at tooling/graders/v2/).
DEFAULT_BRIEF = Path(__file__).resolve().parents[3] / "tooling" / "tasks" / "v2" / "task_triage.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_urgency_vocab(brief_path: Path) -> list[str]:
    """Parse the closed urgency vocabulary from the brief's '## Urgency' section.

    The brief lists each level as a bullet of the form:  - `urgent` — ...
    Parsing stops at the next '## ' heading.
    """
    vocab: list[str] = []
    in_section = False
    for line in brief_path.read_text().splitlines():
        if line.startswith("## "):
            in_section = line.lower().startswith("## urgency")
            continue
        if in_section:
            m = re.match(r"^-\s*`([^`]+)`", line)
            if m:
                vocab.append(m.group(1))
    if not vocab:
        raise ValueError(f"no urgency vocabulary found in {brief_path} (missing '## Urgency' bullet list)")
    return vocab


def grade(workspace: Path, ground_truth_path: Path, brief_path: Path = None) -> dict:
    brief_path = Path(brief_path) if brief_path else DEFAULT_BRIEF
    urgency_vocab = parse_urgency_vocab(brief_path)

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

    # Fixture guard: every ground-truth urgency label must be in the brief's
    # closed vocabulary. A violation is a grader/fixture defect (this is
    # exactly what D3 was), not an agent error — abort loudly.
    bad_gt = {tid: lbl["urgency"] for tid, lbl in gt_tickets.items()
              if lbl.get("urgency") not in urgency_vocab}
    if bad_gt:
        raise ValueError(
            f"ground truth {ground_truth_path} uses urgency labels outside the "
            f"brief vocabulary {urgency_vocab}: {bad_gt}"
        )

    # Per-ticket accuracy
    correct_category = 0
    correct_urgency = 0
    category_errors = []
    urgency_errors = []
    invalid_urgency_labels = []
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
        if a_urg not in urgency_vocab:
            # Out-of-vocabulary agent label: always an urgency error, and
            # reported separately so vocabulary violations are visible.
            invalid_urgency_labels.append({"id": tid, "predicted": a_urg})
            urgency_errors.append({"id": tid, "predicted": a_urg, "actual": gt_urg,
                                   "note": "not in brief urgency vocabulary"})
        elif a_urg == gt_urg:
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
        "grader_version": 2,
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
        "urgency_vocabulary": {
            "labels": urgency_vocab,
            "source_brief": str(brief_path),
            "source_brief_sha256": sha256_file(brief_path),
        },
        "inputs": {
            "ground_truth": str(ground_truth_path),
            "ground_truth_sha256": sha256_file(Path(ground_truth_path)),
        },
        "errors": {
            "missing_tickets": missing_tickets,
            "category_errors": category_errors,
            "urgency_errors": urgency_errors,
            "invalid_urgency_labels": invalid_urgency_labels,
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
    ap.add_argument("--brief", default=None,
                    help="task brief to parse the urgency vocabulary from "
                         f"(default: {DEFAULT_BRIEF})")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    result = grade(Path(args.workspace), Path(args.ground_truth),
                   Path(args.brief) if args.brief else None)
    out_path = Path(args.out) if args.out else (Path(args.workspace) / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
