#!/usr/bin/env python3
"""Mechanically validate an MMBT frozen-75-PR audit repository."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path


PR_REF = re.compile(r"#?\b(\d{3,4})\b")
VERDICT = re.compile(r"\b(merge|revise|reject)\b", re.IGNORECASE)
SOURCE_PATH = re.compile(
    r"(?:[\w.-]+/)*[\w.-]+\.(?:py|sh|bash|js|jsx|ts|tsx|ya?ml|md|json|ps1)(?::\d+)?"
    r"|\b(?:dream-cli|dream-host-agent)\b",
    re.IGNORECASE,
)
BOUNTY_DECLARATION = re.compile(
    r"(?:\*\*)?bounty(?:\s+tier|-tier\s+fit)?(?:\*\*)?\s*:\s*"
    r"(small|medium|large|none|unknown|not[- ]claimed)",
    re.IGNORECASE,
)


def nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def refs(text: str, canonical: set[int]) -> set[int]:
    return {int(match.group(1)) for match in PR_REF.finditer(text)} & canonical


def expected_overlap_pairs(fixture: Path, canonical: set[int]) -> set[tuple[int, int]]:
    by_file: dict[str, set[int]] = defaultdict(set)
    for number in canonical:
        path = fixture / "prs" / f"pr-{number}" / "files.txt"
        if not nonempty(path):
            continue
        for line in path.read_text(errors="replace").splitlines():
            name = line.strip()
            if name:
                by_file[name].add(number)
    pairs: set[tuple[int, int]] = set()
    for numbers in by_file.values():
        pairs.update(itertools.combinations(sorted(numbers), 2))
    return pairs


def fixture_file_sets(fixture: Path, canonical: set[int]) -> dict[int, set[str]]:
    result: dict[int, set[str]] = {}
    for number in canonical:
        path = fixture / "prs" / f"pr-{number}" / "files.txt"
        result[number] = {
            line.strip()
            for line in path.read_text(errors="replace").splitlines()
            if line.strip()
        } if nonempty(path) else set()
    return result


def overlap_pairs(file_sets: dict[int, set[str]]) -> set[tuple[int, int]]:
    by_file: dict[str, set[int]] = defaultdict(set)
    for number, names in file_sets.items():
        for name in names:
            by_file[name].add(number)
    pairs: set[tuple[int, int]] = set()
    for numbers in by_file.values():
        pairs.update(itertools.combinations(sorted(numbers), 2))
    return pairs


def mentioned_pairs(text: str, canonical: set[int]) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for line in text.splitlines():
        numbers = sorted(refs(line, canonical))
        pairs.update(itertools.combinations(numbers, 2))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--transcript", type=Path)
    args = parser.parse_args()
    root = args.workspace.resolve()
    fixture = args.fixture.resolve()
    canonical_list = fixture / "canonical-prs.txt"
    canonical = {
        int(line.strip())
        for line in canonical_list.read_text().splitlines()
        if line.strip()
    }

    failures: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, object] = {"canonical_prs": len(canonical)}

    if len(canonical) != 75:
        failures.append(f"fixture canonical count is {len(canonical)}, expected 75")

    required_root = [
        "README.md",
        "sources.md",
        "tool-log.md",
        "report/executive-summary.md",
        "report/backlog-strategy.md",
        "report/contributor-notes.md",
        "report/project-health.md",
        "analysis/dependency-graph.md",
        "analysis/risk-matrix.md",
        "analysis/surface-area.md",
        "testing/baseline.md",
        "research/questions.md",
        "research/dead-ends.md",
        "research/upstream-context.md",
    ]
    for rel in required_root:
        if not nonempty(root / rel):
            failures.append(f"missing or empty required artifact: {rel}")
    if not (root / "decisions").is_dir() or not any((root / "decisions").glob("*")):
        failures.append("missing non-empty decisions directory")
    if not (root / "analysis/scripts").is_dir() or not any((root / "analysis/scripts").glob("*")):
        failures.append("missing non-empty analysis/scripts directory")

    actual: set[int] = set()
    prs_root = root / "prs"
    if prs_root.is_dir():
        for path in prs_root.iterdir():
            match = re.fullmatch(r"pr-(\d+)", path.name)
            if path.is_dir() and match:
                actual.add(int(match.group(1)))
    missing = sorted(canonical - actual)
    extra = sorted(actual - canonical)
    metrics.update(actual_pr_dirs=len(actual), missing_pr_dirs=missing, extra_pr_dirs=extra)
    if missing:
        failures.append(f"missing PR directories: {missing}")
    if extra:
        failures.append(f"out-of-scope PR directories: {extra}")

    required_pr_files = [
        "verdict.md",
        "summary.md",
        "review.md",
        "diff-analysis.md",
        "interactions.md",
        "trace.md",
    ]
    verdict_counts = defaultdict(int)
    weak_trace: list[int] = []
    weak_review: list[int] = []
    placeholders: list[int] = []
    missing_bounty: list[int] = []
    weak_tests: list[int] = []
    for number in sorted(canonical):
        pr_dir = prs_root / f"pr-{number}"
        for name in required_pr_files:
            if not nonempty(pr_dir / name):
                failures.append(f"PR {number}: missing or empty {name}")
        verdict_text = (pr_dir / "verdict.md").read_text(errors="replace") if nonempty(pr_dir / "verdict.md") else ""
        all_pr_text = "\n".join(
            (pr_dir / name).read_text(errors="replace")
            for name in required_pr_files
            if nonempty(pr_dir / name)
        )
        if "to be filled" in all_pr_text.lower() or "pending (merge" in all_pr_text.lower():
            placeholders.append(number)
        matches = {match.group(1).lower() for match in VERDICT.finditer(verdict_text)}
        headline = VERDICT.search(verdict_text[:1200])
        if not headline:
            failures.append(f"PR {number}: no merge/revise/reject disposition near verdict start")
        else:
            verdict_counts[headline.group(1).lower()] += 1
        if len(matches) > 1:
            warnings.append(f"PR {number}: multiple disposition words appear in verdict ({sorted(matches)})")
        if not BOUNTY_DECLARATION.search(verdict_text):
            missing_bounty.append(number)

        trace_text = (pr_dir / "trace.md").read_text(errors="replace") if nonempty(pr_dir / "trace.md") else ""
        trace_has_source = bool(SOURCE_PATH.search(trace_text))
        trace_has_frozen_pointer = any(token in trace_text for token in ("diff.patch", "@@", "/input/repo"))
        if not (trace_has_source or trace_has_frozen_pointer):
            weak_trace.append(number)

        review_text = (pr_dir / "review.md").read_text(errors="replace") if nonempty(pr_dir / "review.md") else ""
        if not (SOURCE_PATH.search(review_text) or "@@" in review_text or "diff.patch" in review_text):
            weak_review.append(number)

        tests_dir = pr_dir / "tests"
        test_files = [path for path in tests_dir.glob("**/*") if nonempty(path)] if tests_dir.is_dir() else []
        if not test_files:
            failures.append(f"PR {number}: no non-empty test-evidence file")
        else:
            test_text = "\n".join(path.read_text(errors="replace") for path in test_files).lower()
            has_execution = any(token in test_text for token in ("command", "exit", "pass", "fail", "baseline"))
            has_skip = any(token in test_text for token in ("skip", "not run", "not applicable", "unavailable"))
            if not (has_execution or has_skip):
                weak_tests.append(number)

    metrics["verdict_counts"] = dict(sorted(verdict_counts.items()))
    if sum(verdict_counts.values()) != 75:
        failures.append(f"parsed verdict total is {sum(verdict_counts.values())}, expected 75")
    if weak_trace:
        failures.append(f"PRs without a source-file or frozen-diff trace pointer: {weak_trace}")
    if weak_review:
        failures.append(f"PRs whose review has no source-file/diff citation: {weak_review}")
    if placeholders:
        failures.append(f"PRs retaining pending/to-be-filled placeholders: {placeholders}")
    if missing_bounty:
        failures.append(f"PRs without an explicit bounty-tier declaration: {missing_bounty}")
    if weak_tests:
        failures.append(f"PRs with neither execution nor explicit skip evidence: {weak_tests}")

    coverage_files = {
        "risk_matrix": root / "analysis/risk-matrix.md",
        "surface_area": root / "analysis/surface-area.md",
    }
    for label, path in coverage_files.items():
        if nonempty(path):
            missing_refs = sorted(canonical - refs(path.read_text(errors="replace"), canonical))
            metrics[f"{label}_missing_pr_refs"] = missing_refs
            if missing_refs:
                failures.append(f"{label} omits PRs: {missing_refs}")

    dep_path = root / "analysis/dependency-graph.md"
    conflict_path = root / "analysis/conflict-pairs.md"
    raw_expected_pairs = expected_overlap_pairs(fixture, canonical)
    listed_pairs: set[tuple[int, int]] = set()
    dependency_text = ""
    if nonempty(dep_path):
        dependency_text += dep_path.read_text(errors="replace") + "\n"
    if nonempty(conflict_path):
        dependency_text += conflict_path.read_text(errors="replace") + "\n"
    listed_pairs = mentioned_pairs(dependency_text, canonical)

    metadata = json.loads((fixture / "pr-metadata-full.json").read_text())
    metadata_by_number = {
        int(row["number"]): row
        for row in metadata
        if isinstance(row, dict) and str(row.get("number", "")).isdigit()
    }
    raw_file_sets = fixture_file_sets(fixture, canonical)
    trusted_numbers = {
        number
        for number, names in raw_file_sets.items()
        if number in metadata_by_number
        and len(names) == int(metadata_by_number[number].get("changedFiles", -1))
    }
    trusted_pairs = overlap_pairs({n: raw_file_sets[n] for n in trusted_numbers})
    missing_trusted_pairs = sorted(trusted_pairs - listed_pairs)
    missing_raw_pairs = sorted(raw_expected_pairs - listed_pairs)
    metrics.update(
        raw_frozen_file_overlap_pairs=len(raw_expected_pairs),
        trusted_file_list_prs=len(trusted_numbers),
        trusted_file_overlap_pairs=len(trusted_pairs),
        listed_pair_mentions=len(listed_pairs),
        missing_trusted_file_overlap_pairs=len(missing_trusted_pairs),
        missing_trusted_file_overlap_pair_sample=missing_trusted_pairs[:50],
        missing_raw_frozen_overlap_pairs=len(missing_raw_pairs),
        missing_raw_frozen_overlap_pair_sample=missing_raw_pairs[:50],
    )
    if missing_trusted_pairs:
        failures.append(
            f"dependency analysis omits {len(missing_trusted_pairs)}/{len(trusted_pairs)} "
            "high-confidence file-overlap pairs"
        )
    if missing_raw_pairs:
        warnings.append(
            f"dependency analysis does not enumerate {len(missing_raw_pairs)}/"
            f"{len(raw_expected_pairs)} raw frozen-file pairs; raw lists include known reverse-drift, "
            "so this is reported separately and is not itself a semantic failure"
        )

    drift_mismatches = sorted(canonical - trusted_numbers)
    drift_docs = "\n".join(
        path.read_text(errors="replace")
        for path in [root / "README.md", *sorted((root / "decisions").glob("*.md"))]
        if nonempty(path)
    ).lower()
    metrics["raw_file_count_metadata_mismatch_prs"] = drift_mismatches
    if drift_mismatches and not any(term in drift_docs for term in ("reverse-drift", "reverse drift", "baseline drift")):
        failures.append(
            "frozen files.txt counts disagree with metadata for PRs, but the audit does not document "
            "the baseline/reverse-drift limitation"
        )

    if args.transcript:
        transcript_tool_events = 0
        for line in args.transcript.read_text(errors="replace").splitlines():
            try:
                transcript_tool_events += json.loads(line).get("type") == "tool"
            except Exception:
                continue
        tool_log_text = (root / "tool-log.md").read_text(errors="replace") if nonempty(root / "tool-log.md") else ""
        numbered_tool_log_entries = sum(
            bool(re.match(r"^\s*\d+[.)]\s+", line))
            for line in tool_log_text.splitlines()
        )
        metrics.update(
            transcript_tool_events=transcript_tool_events,
            numbered_tool_log_entries=numbered_tool_log_entries,
        )
        if numbered_tool_log_entries < transcript_tool_events:
            failures.append(
                f"tool log records {numbered_tool_log_entries}/{transcript_tool_events} transcript tool events"
            )

    result = {
        "schema_version": 1,
        "workspace": str(root),
        "fixture": str(fixture),
        "pass": not failures,
        "metrics": metrics,
        "failures": failures,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
