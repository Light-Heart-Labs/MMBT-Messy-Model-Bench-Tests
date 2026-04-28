#!/usr/bin/env python3
"""Writing/editing grader: programmatic word-count + must-include / must-not-include
keyword scan per audience. Hand-rating placeholders for tone fit and prose quality.

Usage:
    phase3_writing_editing_grade.py <workspace_dir> <audience_briefs_path> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


# Per-audience keyword bundles for must_not_include checks.
PROHIBITED_PER_AUDIENCE = {
    "ceo_brief": [
        # No "sorry Sarah" / informal apologies
        "sorry sarah",
        # No engineering-jargon-without-translation
        "internal limiter", "fraction-against-MAX", "fraction against MAX",
    ],
    "customer_email": [
        # No named-employee blame
        "marcus", "priya",
        # No internal candor about board / second outage framing
        "second outage", "second 4-hour", "second 4 hour", "board-level",
        "second occurrence", "two outages",
        # No engineering jargon
        "internal limiter", "rate limiter", "throttle rate", "internal metrics",
        "MAX value", "hard-coded MAX", "fraction-against-MAX",
        # No corporate hedging
        "abundance of caution", "unforeseen circumstances",
    ],
    "legal_summary": [
        # No marketing language
        "trust", "we're committed", "we are committed",
        # No named-employee blame
        "marcus",
        # No informal candor
        "sorry sarah", "to be fair",
        # No future-outage speculation
        "future outage", "next outage", "third outage",
    ],
}


REQUIRED_PER_AUDIENCE = {
    "ceo_brief": [
        # one-line summary
        ["outage", "incident"],  # at least one
        # scope
        ["11,400", "11400"],  # accounts impacted
        # second-occurrence framing
        ["second", "two", "twice"],  # board-signal
        ["90 days", "90-day", "second time", "second 4"],
    ],
    "customer_email": [
        # scope acknowledgement
        ["outage", "downtime", "incident"],
        # SLA credit reference
        ["sla", "credit"],
        # contact path
        ["contact", "csm", "support", "reach out", "email"],
    ],
    "legal_summary": [
        # exact time window
        ["14:11", "14:09", "18:24", "14:00"],  # incident times
        # SLA threshold
        ["99.9", "monthly uptime", "uptime"],
        # 4 known-broken-downstream cases
        ["four", "4", "downstream"],
    ],
}


def grade_audience(workspace: Path, audience: str, brief: dict) -> dict:
    fname = brief["filename"]
    path = workspace / fname
    if not path.exists():
        return {"verdict": "MISSING", "filename": fname}
    text = path.read_text()
    wc = word_count(text)
    max_words = brief.get("max_words", 9999)
    norm = text.lower()

    # Required content checks (each entry is a list — at least one keyword from each list must appear)
    required_groups = REQUIRED_PER_AUDIENCE.get(audience, [])
    required_hits = []
    for group in required_groups:
        hit = next((kw for kw in group if kw.lower() in norm), None)
        required_hits.append({"any_of": group, "matched": hit})
    required_pass = all(h["matched"] for h in required_hits)

    # Prohibited content checks (must NOT contain any)
    prohibited = PROHIBITED_PER_AUDIENCE.get(audience, [])
    prohibited_hits = [kw for kw in prohibited if kw.lower() in norm]
    prohibited_pass = (len(prohibited_hits) == 0)

    return {
        "verdict": "PASS" if (required_pass and prohibited_pass and wc <= max_words) else "FAIL",
        "filename": fname,
        "word_count": wc,
        "max_words": max_words,
        "within_word_limit": wc <= max_words,
        "required_content_hits": required_hits,
        "required_content_pass": required_pass,
        "prohibited_content_hits": prohibited_hits,
        "prohibited_content_pass": prohibited_pass,
    }


def grade(workspace: Path, briefs_path: Path) -> dict:
    spec = json.loads(briefs_path.read_text())
    audiences = spec["audiences"]
    per_audience = {}
    all_pass = True
    for aud, brief in audiences.items():
        r = grade_audience(workspace, aud, brief)
        per_audience[aud] = r
        if r["verdict"] != "PASS":
            all_pass = False
    return {
        "task": "writing_editing",
        "verdict": "PASS" if all_pass else "FAIL",
        "per_audience": per_audience,
        "hand_rating_placeholders": {
            "ceo_tone_fit_1to5": None,
            "customer_tone_fit_1to5": None,
            "legal_tone_fit_1to5": None,
            "faithfulness_1to5": None,
            "fabrication_count": None,
            "rater_notes": None,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("audience_briefs")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = grade(Path(args.workspace), Path(args.audience_briefs))
    out_path = Path(args.out) if args.out else (Path(args.workspace) / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
