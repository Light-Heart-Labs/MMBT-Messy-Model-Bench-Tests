#!/usr/bin/env python3
"""Market-research grader: programmatic structural-checks + extensive
hand-rating placeholders. Most of the value is in hand verification of
citations.

Programmatic checks:
- Did the agent produce all required files?
- Did the recommendation specify a product + tier + pricing?
- Are there any obviously hallucinated numbers (claims without nearby [N] citation)?
- How many distinct URLs were cited in sources.md?

The fabricated-stats count and citation-validity score require manual
verification — the grader emits placeholders.

Usage:
    phase3_market_research_grade.py <workspace_dir> <rubric_path> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def grade(workspace: Path, rubric_path: Path) -> dict:
    rec = workspace / "recommendation.md"
    comp = workspace / "comparison.md"
    sources = workspace / "sources.md"

    missing_files = []
    for p, name in [(rec, "recommendation.md"), (comp, "comparison.md"), (sources, "sources.md")]:
        if not p.exists():
            missing_files.append(name)
    if rec.exists():
        rec_text = rec.read_text()
        rec_words = len(re.findall(r"\b\w+\b", rec_text))
    else:
        rec_text = ""
        rec_words = 0

    sources_text = sources.read_text() if sources.exists() else ""
    # Count distinct URLs cited in sources.md
    urls = set(re.findall(r"https?://[^\s\)\]]+", sources_text))

    # Detect inline citations like [1], [2], [3] in recommendation
    inline_cites = set(re.findall(r"\[(\d+)\]", rec_text))
    inline_cite_count = len(inline_cites)

    # Detect specific product naming + tier + pricing
    has_product_name = bool(re.search(
        r"\b(1Password|Bitwarden|Dashlane|Keeper|LastPass|Vault\b)",
        rec_text, re.IGNORECASE
    ))
    has_tier = bool(re.search(r"\b(Business|Teams|Enterprise|Pro|Premium|Family)\b", rec_text))
    has_pricing = bool(re.search(r"\$\d", rec_text))
    has_50_seat_math = bool(re.search(
        r"50\s*(?:seat|user|engineer|employee).*\$|\$.*50\s*(?:seat|user|engineer|employee)",
        rec_text
    ))

    # Soft signal: products evaluated in comparison.md
    comp_text = comp.read_text() if comp.exists() else ""
    products_named = set()
    for product in ["1Password", "Bitwarden", "Dashlane", "Keeper", "LastPass"]:
        if re.search(rf"\b{product}\b", comp_text, re.IGNORECASE):
            products_named.add(product.lower())

    # Programmatic auto-PASS criteria — necessary but NOT sufficient (citations
    # need hand-verification for the substantive PASS):
    auto_pass = (
        len(missing_files) == 0
        and has_product_name
        and has_tier
        and has_pricing
        and len(products_named) >= 4
        and len(urls) >= 6  # at least a handful of cited URLs
    )

    return {
        "task": "market_research",
        "verdict": "STRUCTURAL_PASS" if auto_pass else "STRUCTURAL_FAIL",
        "structural_checks": {
            "missing_files": missing_files,
            "recommendation_word_count": rec_words,
            "has_specific_product_name": has_product_name,
            "has_tier_name": has_tier,
            "has_pricing": has_pricing,
            "has_50_seat_math": has_50_seat_math,
            "products_evaluated_in_comparison": sorted(products_named),
            "products_evaluated_count": len(products_named),
            "inline_citation_count": inline_cite_count,
            "distinct_urls_cited": len(urls),
        },
        "hand_rating_placeholders": {
            "_HAND_VERIFICATION_REQUIRED_": "structural pass is necessary but not sufficient. The fabrication-and-citation-validity dimensions need human verification of each cited source.",
            "citations_valid_pct_0to100": None,
            "fabricated_stats_count": None,
            "products_actually_compared_0to5": None,
            "decision_criteria_explicit_1to5": None,
            "recommendation_specificity_1to5": None,
            "context_appropriateness_1to5": None,
            "rater_notes": None,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("rubric")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = grade(Path(args.workspace), Path(args.rubric))
    out_path = Path(args.out) if args.out else (Path(args.workspace) / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
