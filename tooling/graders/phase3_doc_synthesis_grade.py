#!/usr/bin/env python3
"""Doc-synthesis grader: programmatic fact-coverage check on the brief +
dimensions for hand-rating prose quality.

The grader is semi-automatic — programmatic checks emit a fact_coverage
score; the hand-rating side emits placeholder fields a human fills in
later.

Usage:
    phase3_doc_synthesis_grade.py <workspace_dir> <key_facts_path> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


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
    word_count = len(re.findall(r"\b\w+\b", brief))
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

    # Programmatic pass criterion: capture >= 6 of 8 facts AND <= 700 words
    coverage_threshold = 6
    word_limit = 700
    auto_verdict = (
        "PASS" if (captured >= coverage_threshold and word_count <= word_limit)
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
        "verdict": auto_verdict,
        "scores": {
            "fact_coverage": coverage_score,
            "facts_captured": captured,
            "facts_total": n,
            "word_count": word_count,
            "word_limit": word_limit,
            "within_word_limit": word_count <= word_limit,
        },
        "thresholds": {
            "min_facts_captured": coverage_threshold,
            "max_word_count": word_limit,
        },
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
