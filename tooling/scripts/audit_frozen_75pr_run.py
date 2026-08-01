#!/usr/bin/env python3
"""Create a uniform independent audit overlay for one frozen-75 MMBT run."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path


SOURCE_CITE = re.compile(
    r"(?:[\w.-]+/)*[\w.-]+\.(?:py|sh|bash|js|jsx|ts|tsx|ya?ml|md|json|ps1)(?::\d+)?"
    r"|\b(?:dream-cli|dream-host-agent)\b",
    re.IGNORECASE,
)
BOUNTY_DECLARATION = re.compile(
    r"(?:\*\*)?bounty(?:\s+tier|-tier\s+fit)?(?:\*\*)?\s*:\s*"
    r"(small|medium|large|none|unknown|not[- ]claimed)",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(errors="replace"))


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_dir", type=Path)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("validator", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    log_dir = args.log_dir.resolve()
    workspace = args.workspace.resolve()
    fixture = args.fixture.resolve()
    validator = args.validator.resolve()
    output = args.output or (log_dir / "75pr_audit.json")

    summary = read_json(log_dir / "summary.json")
    receipt = read_json(log_dir / "receipt.json")
    cost = read_json(log_dir / "cost.json") if (log_dir / "cost.json").exists() else {}
    telemetry = read_json(log_dir / "gpu_telemetry.json") if (log_dir / "gpu_telemetry.json").exists() else {}
    transcript = log_dir / "transcript.jsonl"

    validation = subprocess.run(
        [
            "python3",
            str(validator),
            str(workspace),
            str(fixture),
            "--transcript",
            str(transcript),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    structural = json.loads(validation.stdout)

    prs = sorted((workspace / "prs").glob("pr-*"), key=lambda path: int(path.name[3:]))
    reviews = {int(path.name[3:]): (path / "review.md").read_text(errors="replace") for path in prs}
    traces = {int(path.name[3:]): (path / "trace.md").read_text(errors="replace") for path in prs}
    diffs = {int(path.name[3:]): (path / "diff-analysis.md").read_text(errors="replace") for path in prs}
    verdicts = {int(path.name[3:]): (path / "verdict.md").read_text(errors="replace") for path in prs}
    test_prs = sorted(
        {
            int(path.parents[1].name[3:])
            for path in (workspace / "prs").glob("pr-*/tests/**/*")
            if path.is_file() and path.stat().st_size > 0
        }
    )

    transcript_rows = []
    for line in transcript.read_text(errors="replace").splitlines():
        try:
            transcript_rows.append(json.loads(line))
        except Exception:
            continue
    tool_events = sum(row.get("type") == "tool" for row in transcript_rows)
    tool_log = (workspace / "tool-log.md").read_text(errors="replace")
    numbered_tool_entries = sum(
        bool(re.match(r"^\s*\d+[.)]\s+", line)) for line in tool_log.splitlines()
    )

    archive = log_dir / "workspace_final.tar.gz"
    with gzip.open(archive, "rb") as stream:
        while stream.read(1024 * 1024):
            pass
    tags = command("git", "-C", str(workspace), "tag").splitlines()
    head = command("git", "-C", str(workspace), "rev-parse", "HEAD")
    tag_targets = {
        tag: command("git", "-C", str(workspace), "rev-list", "-n1", tag)
        for tag in tags
    }

    shallow_reviews = sorted(number for number, text in reviews.items() if len(text.encode()) < 800)
    review_citations = sorted(number for number, text in reviews.items() if SOURCE_CITE.search(text))
    actual_bounty = sorted(number for number, text in verdicts.items() if BOUNTY_DECLARATION.search(text))

    legacy_shipped = (
        summary.get("finish_reason") == "done_signal"
        and len(prs) == 75
        and bool(tags)
        and not command("git", "-C", str(workspace), "status", "--porcelain")
    )
    if not legacy_shipped:
        classification = "MODEL_TERMINAL_FAILURE"
    elif len(test_prs) < 38 or len(shallow_reviews) >= 38:
        classification = "SCAFFOLD_AND_STOP"
    elif not structural.get("pass"):
        classification = "SHIPPED_WITH_MATERIAL_AUDIT_DEFECTS"
    else:
        # Mechanical success is necessary, not sufficient; retain a manual
        # review gate before assigning SUBSTANTIVE_PASS.
        classification = "MECHANICAL_PASS_REQUIRES_MANUAL_SUBSTANCE_REVIEW"

    result = {
        "schema_version": 2,
        "audited_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "run_name": summary.get("model", "unknown") + " " + log_dir.name,
        "classification": classification,
        "legacy_shipped": legacy_shipped,
        "verdict_counts": structural.get("metrics", {}).get("verdict_counts", {}),
        "runtime": {
            "wall_s": summary.get("elapsed_s"),
            "iterations": summary.get("iterations"),
            "completion_tokens": summary.get("total_completion_tokens"),
            "prompt_tokens": summary.get("total_prompt_tokens"),
            "completion_tps_model_call": cost.get("throughput", {}).get("completion_tps_avg"),
        },
        "artifact_integrity": {
            "archive_sha256": sha256(archive),
            "archive_bytes": archive.stat().st_size,
            "archive_gzip_valid": True,
            "head": head,
            "tags": tags,
            "tag_targets": tag_targets,
            "tag_at_head": head in tag_targets.values(),
            "clean": not command("git", "-C", str(workspace), "status", "--porcelain"),
            "commit_count": int(command("git", "-C", str(workspace), "rev-list", "--count", "HEAD")),
        },
        "substance": {
            "test_evidence_count": len(test_prs),
            "test_evidence_prs": test_prs,
            "missing_test_or_skip_count": 75 - len(test_prs),
            "missing_test_or_skip_prs": sorted(set(verdicts) - set(test_prs)),
            "reviews_under_800_bytes_count": len(shallow_reviews),
            "reviews_under_800_bytes_prs": shallow_reviews,
            "reviews_with_source_citation_count": len(review_citations),
            "reviews_with_source_citation_prs": review_citations,
            "reviews_with_hunk_marker_count": sum("@@" in text for text in reviews.values()),
            "traces_with_source_citation_count": sum(bool(SOURCE_CITE.search(text)) for text in traces.values()),
            "traces_with_hunk_marker_count": sum("@@" in text for text in traces.values()),
            "diff_analyses_with_hunk_marker_count": sum("@@" in text for text in diffs.values()),
            "explicit_actual_bounty_tier_count": len(actual_bounty),
            "explicit_actual_bounty_tier_prs": actual_bounty,
            "transcript_tool_events": tool_events,
            "numbered_tool_log_entries": numbered_tool_entries,
        },
        "strict_validation": structural,
        "telemetry": telemetry,
        "evidence": {
            "summary_sha256": sha256(log_dir / "summary.json"),
            "receipt_sha256": sha256(log_dir / "receipt.json"),
            "transcript_sha256": sha256(transcript),
            "validator_sha256": sha256(validator),
            "task_sha256": receipt.get("task", {}).get("sha256"),
            "fixture_path": str(fixture),
        },
    }
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": sha256(output),
                "classification": classification,
                "tests": len(test_prs),
                "shallow_reviews": len(shallow_reviews),
                "strict_pass": structural.get("pass"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
