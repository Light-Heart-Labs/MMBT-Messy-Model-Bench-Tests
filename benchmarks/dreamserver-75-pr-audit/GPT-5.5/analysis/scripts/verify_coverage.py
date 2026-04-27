#!/usr/bin/env python3
"""Verify that every audited PR directory has the required file set."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED = [
    "verdict.md",
    "summary.md",
    "review.md",
    "tests/results.md",
    "diff-analysis.md",
    "interactions.md",
    "trace.md",
]


def main() -> int:
    index = json.loads((ROOT / "analysis" / "pr-index.json").read_text(encoding="utf-8"))
    numbers = sorted(int(item["number"]) for item in index)
    errors: list[str] = []

    if len(numbers) != 75:
        errors.append(f"expected 75 PRs in analysis/pr-index.json, found {len(numbers)}")

    for number in numbers:
        pr_dir = ROOT / "prs" / f"pr-{number}"
        if not pr_dir.is_dir():
            errors.append(f"missing directory {pr_dir.relative_to(ROOT)}")
            continue
        for rel in REQUIRED:
            path = pr_dir / rel
            if not path.is_file():
                errors.append(f"missing {path.relative_to(ROOT)}")

    if errors:
        print("coverage check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"coverage check passed: {len(numbers)} PRs, {len(REQUIRED)} required artifacts each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
