#!/usr/bin/env python3
"""Project-management grader: programmatic recall checks for the expected
workstreams / risks / decisions / milestones, plus hand-rating placeholders.

Usage:
    phase3_project_mgmt_grade.py <workspace_dir> <expected_path> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower())


# Per-item keyword bundles: at least one must appear in the report.
WORKSTREAM_KEYWORDS = {
    "WS1": ["query layer", "query-layer", "filter parser", "sdk filter"],
    "WS2": ["dashboard refresh", "frontend", "mobile-responsive", "mobile responsive"],
    "WS3": ["panel-density", "architectural fix", "40-panel", "40 panel", "panel density"],
    "WS4": ["access-control", "access control", "iam", "private-beta", "private beta"],
    "WS5": ["maevia", "csm call", "customer comms", "promised ga"],
    "WS6": ["legal", "private-beta contract", "contract draft"],
}

RISK_KEYWORDS = {
    "R1": ["mid-july slip", "timeline slip", "iam slip", "schedule risk", "could slip"],
    "R2": ["maevia push", "maevia push-back", "maevia pushback", "expectations gap"],
    "R3": ["legal unresponsive", "legal silent", "legal hasn't", "blocking on legal"],
    "R4": ["40-panel", "40 panel", "panel limit", "expectation mismatch", "customer-facing docs"],
    "R5": ["custom-branding", "custom branding", "deferred", "v1.5 bleed"],
    "R6": ["reviewer bottleneck", "single point", "lin's pto", "lin pto"],
}

DECISION_KEYWORDS = {
    "D1_branding": ["branding deferred", "cut custom-branding", "cut custom branding", "branding cut"],
    "D2_panel_limit": ["40-panel", "40 panel", "panel limit"],
    "D3_mobile": ["mobile responsive", "web responsive", "native v2", "native in v2", "responsive in v1"],
    "D4_option_b": ["option b", "private beta with", "private-beta with"],
}

MILESTONE_KEYWORDS = {
    "M1": ["mid-may", "mid may", "may 2026"],  # query-layer complete
    "M2": ["mid-may", "mid may"],  # mobile-responsive
    "M3": ["mid-july", "mid july", "july 2026", "v1 launch"],  # V1 launch
    "M4": ["v1.1", "august", "september"],  # architectural fix
    "M5": ["v1.5", "deferred", "tbd"],  # custom-branding + native mobile
}


def grade(workspace: Path, expected_path: Path) -> dict:
    report = workspace / "status_report.md"
    if not report.exists():
        return {"task": "project_mgmt", "verdict": "MISSING_OUTPUT",
                "notes": "no status_report.md in workspace"}

    text = report.read_text()
    norm = normalize(text)
    word_count = len(re.findall(r"\b\w+\b", text))

    # Count unique keyword groups that match
    def match_groups(groups: dict) -> dict:
        results = {}
        for gid, keywords in groups.items():
            hit = next((kw for kw in keywords if normalize(kw) in norm), None)
            results[gid] = {"matched": hit is not None, "keyword": hit}
        return results

    ws_results = match_groups(WORKSTREAM_KEYWORDS)
    risk_results = match_groups(RISK_KEYWORDS)
    decision_results = match_groups(DECISION_KEYWORDS)
    milestone_results = match_groups(MILESTONE_KEYWORDS)

    workstream_recall = sum(1 for r in ws_results.values() if r["matched"])
    risk_recall = sum(1 for r in risk_results.values() if r["matched"])
    decision_recall = sum(1 for r in decision_results.values() if r["matched"])
    milestone_recall = sum(1 for r in milestone_results.values() if r["matched"])

    # Structure check: does the report have clearly labeled sections?
    sections_required = ["workstream", "risk", "decision", "milestone"]
    sections_present = [s for s in sections_required if s in norm]

    # Pass criteria:
    #   workstream_recall >= 4 of 6
    #   risk_recall >= 3 of 6
    #   decision_recall >= 3 of 4
    #   milestone_recall >= 3 of 5
    #   word_count <= 700 (some slack for headers)
    #   3 of 4 required sections clearly named
    auto_pass = (
        workstream_recall >= 4
        and risk_recall >= 3
        and decision_recall >= 3
        and milestone_recall >= 3
        and word_count <= 700
        and len(sections_present) >= 3
    )

    return {
        "task": "project_mgmt",
        "verdict": "PASS" if auto_pass else "FAIL",
        "scores": {
            "workstream_recall": f"{workstream_recall}/6",
            "risk_recall": f"{risk_recall}/6",
            "decision_recall": f"{decision_recall}/4",
            "milestone_recall": f"{milestone_recall}/5",
            "sections_present": sections_present,
            "word_count": word_count,
        },
        "thresholds": {
            "min_workstreams": 4,
            "min_risks": 3,
            "min_decisions": 3,
            "min_milestones": 3,
            "max_word_count": 700,
        },
        "details": {
            "workstreams": ws_results,
            "risks": risk_results,
            "decisions": decision_results,
            "milestones": milestone_results,
        },
        "hand_rating_placeholders": {
            "structure_quality_1to5": None,
            "fabrication_count": None,
            "owner_accuracy_0to6": None,
            "rater_notes": None,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("expected")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = grade(Path(args.workspace), Path(args.expected))
    out_path = Path(args.out) if args.out else (Path(args.workspace) / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
