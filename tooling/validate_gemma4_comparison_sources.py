#!/usr/bin/env python3
"""Fail closed if a pinned Gemma comparison source or extracted claim drifts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


EXPECTED_IDS = {
    "qwen3.6-27b-awq",
    "qwen3-coder-next-awq",
    "qwen3.6-35b-a3b-awq",
    "qwen3.5-397b-a17b-q3-nothink",
    "deepseek-v4-flash-0731",
}
RECEIPTS = {
    "qwen3.6-27b-awq": "benchmarks/microbench-2026-04-28/bug-fixing/Qwen3.6-27B-AWQ/receipt.json",
    "qwen3-coder-next-awq": "benchmarks/microbench-2026-04-28/bug-fixing/Qwen3-Coder-Next-AWQ/receipt.json",
    "qwen3.6-35b-a3b-awq": "benchmarks/dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/receipt.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def git_blob_sha256(root: Path, commit: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{path}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return hashlib.sha256(result.stdout).hexdigest()


def validate(root: Path, manifest_path: Path) -> list[str]:
    errors = []
    manifest = read_json(manifest_path)
    source_commit = manifest.get("source_repository_commit")
    for source in manifest.get("source_documents", []):
        path = root / source["path"]
        if source.get("verify_at_source_commit"):
            observed = git_blob_sha256(root, source_commit, source["path"])
            if observed is None:
                errors.append(f"missing source document at pinned commit: {source['path']}")
            elif observed != source["sha256"]:
                errors.append(f"source hash drift at pinned commit: {source['path']}")
        elif not path.is_file():
            errors.append(f"missing source document: {source['path']}")
        elif sha256(path) != source["sha256"]:
            errors.append(f"source hash drift: {source['path']}")

    ancestor = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", source_commit, "HEAD"],
        capture_output=True,
        check=False,
    )
    if ancestor.returncode != 0:
        errors.append("pinned comparison source commit is not an ancestor of HEAD")

    comparators = {row.get("id"): row for row in manifest.get("comparators", [])}
    if set(comparators) != EXPECTED_IDS:
        errors.append(
            f"comparator ids differ: observed={sorted(comparators)} expected={sorted(EXPECTED_IDS)}"
        )
    for model_id, row in comparators.items():
        canonical = row.get("canonical")
        if canonical is None:
            continue
        total = canonical.get("total")
        for field in ("raw_passes", "corrected_passes"):
            value = canonical.get(field)
            if value is not None and (
                not isinstance(value, int) or not isinstance(total, int) or not 0 <= value <= total
            ):
                errors.append(f"invalid {model_id} {field}/{total}")

    deepseek = read_json(root / "benchmarks/deepseek-v4-flash-0731/canonical-regrade-audit.json")
    pinned = (comparators.get("deepseek-v4-flash-0731") or {}).get("canonical") or {}
    for field, source_field in (
        ("raw_passes", "raw_reported_passes"),
        ("corrected_passes", "corrected_passes"),
        ("total", "total_cells"),
    ):
        if pinned.get(field) != deepseek.get(source_field):
            errors.append(f"DeepSeek extracted {field} differs from its audit")

    qwen397 = read_json(
        root / "benchmarks/deepseek-v4-flash-0731/qwen397-corrected-score-overlay.json"
    )
    pinned = (comparators.get("qwen3.5-397b-a17b-q3-nothink") or {}).get("canonical") or {}
    qwen_raw = (qwen397.get("raw_published") or {}).get("nothink") or {}
    qwen_corrected = (qwen397.get("corrected_overlay") or {}).get("nothink") or {}
    if pinned.get("raw_passes") != qwen_raw.get("pass"):
        errors.append("Qwen3.5-397B extracted raw_passes differs from its overlay")
    if pinned.get("corrected_passes") != qwen_corrected.get("pass"):
        errors.append("Qwen3.5-397B extracted corrected_passes differs from its overlay")
    if pinned.get("total") != qwen_corrected.get("total"):
        errors.append("Qwen3.5-397B extracted total differs from its overlay")

    for model_id, receipt_rel in RECEIPTS.items():
        row = comparators.get(model_id) or {}
        op = row.get("operating_point") or {}
        receipt = read_json(root / receipt_rel)
        defaults = receipt.get("inference_request_defaults") or {}
        if defaults.get("temperature") != op.get("temperature"):
            errors.append(f"{model_id} temperature differs from pinned receipt")
        if defaults.get("max_model_len") != op.get("context_tokens"):
            errors.append(f"{model_id} context differs from pinned receipt")
        ceiling = op.get("historical_per_response_ceiling")
        if ceiling is not None and str(ceiling) not in str(defaults.get("max_tokens_strategy")):
            errors.append(f"{model_id} output ceiling differs from pinned receipt")

    scorecard = (root / "SCORECARD.md").read_text()
    for required in (
        "Qwen3.6-27B-AWQ",
        "Qwen3-Coder-Next-AWQ",
        "Qwen3.6-35B-A3B-AWQ",
        "DeepSeek V4 Flash 0731",
        "397B-A17B",
    ):
        if required not in scorecard:
            errors.append(f"scorecard no longer identifies comparator {required}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--manifest", type=Path,
        default=Path(__file__).with_name("gemma4-comparison-sources.json"),
    )
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.manifest.resolve())
    print(json.dumps({"passed": not errors, "errors": errors}, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
