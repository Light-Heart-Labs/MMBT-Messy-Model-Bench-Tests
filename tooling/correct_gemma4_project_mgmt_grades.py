#!/usr/bin/env python3
"""Create a non-destructive overlay for narrow project-management grader misses."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


RULES = {
    "R2": {
        "description": "Maevia GA-to-private-beta pushback is expressed without one contiguous legacy keyword",
        "patterns": [
            r"\bmaevia\b.{0,240}\b(?:push(?:ed)?[ -]?back|fallout|promis(?:e|ed)\s+ga|private[ -]?beta)\b",
        ],
    },
    "R3": {
        "description": "legal/private-beta contract delay uses an equivalent non-contracted phrase",
        "patterns": [
            r"\blegal\b.{0,200}\b(?:has\s+not|not\s+yet\s+responded|sign[ -]?off|approval|unresponsive|silent|delay|contract)\b",
        ],
    },
    "D3_mobile": {
        "description": "web-responsive V1 and native V2 uses a hyphen the legacy keyword omits",
        "patterns": [
            r"\bweb[ -]?responsive\b.{0,160}\bnative\b.{0,100}\bv2\b",
        ],
    },
    "D4_option_b": {
        "description": "private beta followed by the selected-customer count is Option B",
        "patterns": [
            r"\bprivate[ -]?beta\b.{0,120}\b(?:3\s*[-–]\s*5|selected\s+customers?)\b",
        ],
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_correction(raw: dict, report_text: str) -> tuple[dict, list[dict]]:
    corrected = copy.deepcopy(raw)
    details = corrected.get("details") or {}
    changes = []
    normalized = re.sub(r"\s+", " ", report_text.lower())
    for item, rule in RULES.items():
        category = "risks" if item.startswith("R") else "decisions"
        result = (details.get(category) or {}).get(item)
        if not isinstance(result, dict) or result.get("matched"):
            continue
        matched_pattern = next(
            (pattern for pattern in rule["patterns"] if re.search(pattern, normalized)),
            None,
        )
        if matched_pattern:
            result["matched"] = True
            result["keyword"] = "correction-overlay-semantic-equivalent"
            changes.append({
                "item": item,
                "category": category,
                "reason": rule["description"],
                "pattern": matched_pattern,
            })

    scores = corrected.get("scores") or {}
    thresholds = corrected.get("thresholds") or {}
    workstream_count = sum(
        bool(value.get("matched")) for value in (details.get("workstreams") or {}).values()
    )
    risk_count = sum(
        bool(value.get("matched")) for value in (details.get("risks") or {}).values()
    )
    decision_count = sum(
        bool(value.get("matched")) for value in (details.get("decisions") or {}).values()
    )
    milestone_count = sum(
        bool(value.get("matched")) for value in (details.get("milestones") or {}).values()
    )
    scores["workstream_recall"] = f"{workstream_count}/6"
    scores["risk_recall"] = f"{risk_count}/6"
    scores["decision_recall"] = f"{decision_count}/4"
    scores["milestone_recall"] = f"{milestone_count}/5"
    corrected["verdict"] = "PASS" if (
        workstream_count >= thresholds.get("min_workstreams", 4)
        and risk_count >= thresholds.get("min_risks", 3)
        and decision_count >= thresholds.get("min_decisions", 3)
        and milestone_count >= thresholds.get("min_milestones", 3)
        and scores.get("word_count", 10**9) <= thresholds.get("max_word_count", 700)
        and len(scores.get("sections_present") or []) >= 3
    ) else "FAIL"
    return corrected, changes


def build(root: Path, target_n: int, script_path: Path) -> tuple[dict, list[str]]:
    raw_grader = root / "tooling" / "graders" / "phase3_project_mgmt_grade.py"
    errors = []
    cells = []
    for replicate in range(1, target_n + 1):
        name = f"p3_pm_gemma4-31b-q4_v{replicate}"
        run = root / "logs" / name
        raw_grade = run / "grade.json"
        report = root / "tooling" / "workspace" / name / "status_report.md"
        archive = run / "workspace_final.tar.gz"
        missing = [str(path) for path in (raw_grade, report, archive) if not path.is_file()]
        if missing:
            errors.append(f"{name}: missing {missing}")
            continue
        raw = json.loads(raw_grade.read_text())
        corrected, changes = apply_correction(raw, report.read_text())
        cells.append({
            "run_name": name,
            "raw_grade_sha256": sha256(raw_grade),
            "workspace_archive_sha256": sha256(archive),
            "status_report_sha256": sha256(report),
            "raw_verdict": raw.get("verdict"),
            "corrected_verdict": corrected.get("verdict"),
            "changes": changes,
            "corrected_grade": corrected,
        })
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaign": "gemma4-31b-q4-mmbt",
        "target_n": target_n,
        "scope": "p3_pm legacy lexical false negatives only",
        "policy": "immutable grade.json files remain raw evidence; this overlay changes no run artifact or raw verdict",
        "correction_script": {
            "path": str(script_path.resolve()),
            "sha256": sha256(script_path),
        },
        "raw_grader": {
            "path": str(raw_grader.resolve()),
            "sha256": sha256(raw_grader),
        },
        "rules": RULES,
        "aggregate": {
            "cells": len(cells),
            "raw_passes": sum(cell["raw_verdict"] == "PASS" for cell in cells),
            "corrected_passes": sum(cell["corrected_verdict"] == "PASS" for cell in cells),
            "verdict_changes": sum(
                cell["raw_verdict"] != cell["corrected_verdict"] for cell in cells
            ),
        },
        "cells": cells,
    }, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target-n", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document, errors = build(args.root.resolve(), args.target_n, Path(__file__))
    document["errors"] = errors
    document["passed"] = not errors
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps({**document["aggregate"], "errors": len(errors)}, sort_keys=True))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
