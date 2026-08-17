#!/usr/bin/env python3
r"""Project-management grader, v2.

Provenance: copied from tooling/graders/phase3_project_mgmt_grade.py
(v1, sha256 e1c3a9190e6d19cffd76734c8c922450b22d674bd5fd2db052fef31f91777bca).

Changes vs v1 (PREREGISTRATION.md section 8 / grader-defects.md):

- D1: the regex word counter ``len(re.findall(r"\b\w+\b", text))`` on
  status_report.md is replaced by the ``wc -w`` contract in wordcount_v2.py
  (LC_ALL=C.UTF-8, +-3% tolerance band at the 700-word ceiling), matching the
  counter the v2 task brief (tooling/tasks/v2/task_project_mgmt.md) now names
  explicitly.

- D2: risk R3 (legal / private-beta contract delay) is matched semantically,
  not just by the literal keyword list.  v1 recognised "legal hasn't" but not
  "legal has not": a natural experiment in the prior corpus
  (p3_pm_qwen36-nothink-card_v2/v8 vs _v4, byte-identical table rows except
  the contraction) showed the apostrophe alone deciding PASS vs FAIL.  The
  semantic rule below is adopted verbatim from this repository's existing,
  unit-tested correction module:

      tooling/correct_gemma4_project_mgmt_grades.py, RULES["R3"]["patterns"][0]
      (sha256 86eeec68b6c7114fb0672566220938e35fa605cd1b89ac4b0863f7cfe305f581)

  which had shipped for the Gemma4 campaign but never applied to other
  campaigns because its cell enumeration hardcoded a filename prefix.  Only
  R3 receives semantic treatment: it is the only rule backed by a decisive
  natural experiment.  The upstream module's R2 replacement pattern fires on
  64 of 64 prior-corpus cells (a rubric rewrite, not a false-negative fix),
  so R2, D3_mobile and D4_option_b keyword lists stay as in v1.

Other keyword bundles, thresholds, section checks and CLI are unchanged.

Usage:
    phase3_project_mgmt_grade.py <workspace_dir> <expected_path> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from wordcount_v2 import length_gate


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

# D2: semantic R3-equivalence rule, adopted verbatim (with attribution) from
# tooling/correct_gemma4_project_mgmt_grades.py RULES["R3"]["patterns"][0]
# (sha256 86eeec68b6c7114fb0672566220938e35fa605cd1b89ac4b0863f7cfe305f581).
# Applied to the same normalized text the keyword scan uses (lowercased,
# whitespace collapsed), exactly as the upstream apply_correction() does.
R3_SEMANTIC_PATTERN = (
    r"\blegal\b.{0,200}\b(?:has\s+not|not\s+yet\s+responded|sign[ -]?off|"
    r"approval|unresponsive|silent|delay|contract)\b"
)
R3_SEMANTIC_MARKER = "r3-semantic-equivalent-v2"


def grade(workspace: Path, expected_path: Path) -> dict:
    report = workspace / "status_report.md"
    if not report.exists():
        return {"task": "project_mgmt", "verdict": "MISSING_OUTPUT",
                "notes": "no status_report.md in workspace"}

    text = report.read_text()
    norm = normalize(text)
    # v2 (D1): wc -w under LC_ALL=C.UTF-8, +-3% band at the ceiling.
    word_limit = 700
    length = length_gate(report, word_limit)
    word_count = length["word_count"]

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

    # v2 (D2): R3 semantic equivalence — a literal-keyword miss is re-checked
    # against the upstream semantic pattern before scoring.
    r3_semantic_applied = False
    if not risk_results["R3"]["matched"] and re.search(R3_SEMANTIC_PATTERN, norm):
        risk_results["R3"] = {"matched": True, "keyword": R3_SEMANTIC_MARKER}
        r3_semantic_applied = True

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
    #   status_report.md within the word gate (wc -w <= floor(700 * 1.03) = 721)
    #   3 of 4 required sections clearly named
    auto_pass = (
        workstream_recall >= 4
        and risk_recall >= 3
        and decision_recall >= 3
        and milestone_recall >= 3
        and length["within_word_limit"]
        and len(sections_present) >= 3
    )

    return {
        "task": "project_mgmt",
        "grader_version": 2,
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
            "max_word_count": word_limit,
        },
        "length_gate": length,
        "semantic_rules": {
            "R3": {
                "source": "tooling/correct_gemma4_project_mgmt_grades.py RULES[R3]",
                "source_sha256": "86eeec68b6c7114fb0672566220938e35fa605cd1b89ac4b0863f7cfe305f581",
                "pattern": R3_SEMANTIC_PATTERN,
                "applied": r3_semantic_applied,
            },
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
