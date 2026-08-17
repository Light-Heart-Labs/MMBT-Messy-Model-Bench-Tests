#!/usr/bin/env python3
r"""Doc-synthesis grader, v2.

Provenance: copied from tooling/graders/phase3_doc_synthesis_grade.py
(v1, sha256 8c117c0a3bfec94a91f94e49bb5b4281a458bcc4a650e9ae86e2450f0f5cac0a).

Change vs v1 (defect D1, PREREGISTRATION.md section 8 / grader-defects.md):
the regex word counter ``len(re.findall(r"\b\w+\b", ...))`` on brief.md is
replaced by the ``wc -w`` contract in wordcount_v2.py (LC_ALL=C.UTF-8, +-3%
tolerance band at the 700-word ceiling), matching the counter the v2 task
brief (tooling/tasks/v2/task_doc_synthesis.md) now names explicitly.
Fact matching, soft signals, thresholds and CLI are unchanged from v1.

Usage:
    phase3_doc_synthesis_grade.py <workspace_dir> <key_facts_path> [--out grade.json]
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


def fact_present(brief: str, fact_def: dict) -> tuple[bool, str]:
    """Return (matched, why) for a single planted fact."""
    norm = normalize(brief)
    keywords_any = fact_def.get("match_keywords_any", []) or []
    keywords_all = fact_def.get("match_keywords_all", []) or []
    any_hit = None
    for kw in keywords_any:
        if normalize(kw) in norm:
            any_hit = kw
            break
    all_hit = all(normalize(kw) in norm for kw in keywords_all) if keywords_all else True
    if any_hit and all_hit:
        return (True, f"any:{any_hit}; all:{keywords_all}")
    return (False, f"any={'hit:'+any_hit if any_hit else 'none'}; all_required_count={len(keywords_all)}, all_satisfied={all_hit}")


def grade(workspace: Path, key_facts_path: Path) -> dict:
    brief_path = workspace / "brief.md"
    if not brief_path.exists():
        return {"task": "doc_synthesis", "verdict": "MISSING_OUTPUT",
                "notes": "no brief.md in workspace"}

    brief = brief_path.read_text()
    # v2 (D1): wc -w under LC_ALL=C.UTF-8, +-3% band at the ceiling.
    word_limit = 700
    length = length_gate(brief_path, word_limit)
    word_count = length["word_count"]
    kf = json.loads(key_facts_path.read_text())

    fact_results = {}
    captured = 0
    for fid, fact_def in kf["facts"].items():
        matched, why = fact_present(brief, fact_def)
        fact_results[fid] = {
            "summary": fact_def["summary"],
            "captured": matched,
            "why": why,
        }
        if matched:
            captured += 1

    n = len(kf["facts"])
    coverage_score = round(captured / n, 3)

    # Programmatic pass criterion: capture >= 6 of 8 facts AND within the
    # word gate (wc -w <= floor(700 * 1.03) = 721)
    coverage_threshold = 6
    auto_verdict = (
        "PASS" if (captured >= coverage_threshold and length["within_word_limit"])
        else "FAIL"
    )

    # Soft signals
    citations_present = bool(re.search(r"\[Source\s*\d\]", brief, re.IGNORECASE)) or bool(re.search(r"\[S\d\]", brief))
    recommendation_present = any(
        word in brief.lower()
        for word in ["recommend", "follow-on", "pass", "more diligence", "would invest", "should not", "should invest"]
    )

    return {
        "task": "doc_synthesis",
        "grader_version": 2,
        "verdict": auto_verdict,
        "scores": {
            "fact_coverage": coverage_score,
            "facts_captured": captured,
            "facts_total": n,
            "word_count": word_count,
            "word_limit": word_limit,
            "within_word_limit": length["within_word_limit"],
        },
        "thresholds": {
            "min_facts_captured": coverage_threshold,
            "max_word_count": word_limit,
        },
        "length_gate": length,
        "fact_results": fact_results,
        "soft_signals": {
            "citations_present": citations_present,
            "explicit_recommendation_present": recommendation_present,
        },
        "hand_rating_placeholders": {
            "prose_quality_1to5": None,
            "stance_clarity_1to5": None,
            "source_skepticism_1to5": None,
            "balanced_tone_1to5": None,
            "rater_notes": None,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("key_facts")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = grade(Path(args.workspace), Path(args.key_facts))
    out_path = Path(args.out) if args.out else (Path(args.workspace) / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
