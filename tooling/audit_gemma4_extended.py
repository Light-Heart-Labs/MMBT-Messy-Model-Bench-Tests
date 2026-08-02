#!/usr/bin/env python3
"""Fail-closed provenance and artifact audit for Gemma's extended MMBT suites."""
from __future__ import annotations

import argparse
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from audit_gemma4_campaign import audit_run, read_json, sha256


RUN_PREFIXES = {
    "dreamserver-1-pr-audit": "n1_gemma4-31b-q4",
    "wallstreet-investment-memo": "gemma4-31b-q4_invest_memo",
    "wallstreet-board-presentation": "gemma4-31b-q4_board_pres",
    "dreamserver-75-pr-audit": "gemma4-31b-q4_75pr",
}


def expected_run_name(suite_id: str, rep: int) -> str:
    return f"{RUN_PREFIXES[suite_id]}_v{rep}"


def audit_subject_refs(root: Path, suite: dict, run_dir: Path) -> list[str]:
    """Prove a one-PR artifact audited the pinned comparator subject."""
    errors = []
    pin_path = root / suite["subject_pin"]
    if not pin_path.is_file():
        return [f"subject pin missing: {pin_path}"]
    if sha256(pin_path) != suite["subject_pin_sha256"]:
        errors.append("subject pin hash mismatch")
    archive = run_dir / "workspace_final.tar.gz"
    if not archive.is_file():
        return errors
    text_parts = []
    try:
        with tarfile.open(archive, "r:gz") as handle:
            for member in handle.getmembers():
                if not member.isfile() or member.size > 5 * 1024 * 1024:
                    continue
                if Path(member.name).suffix.lower() not in {".md", ".txt", ".json"}:
                    continue
                extracted = handle.extractfile(member)
                if extracted is not None:
                    text_parts.append(extracted.read().decode(errors="replace").lower())
    except (OSError, tarfile.TarError) as exc:
        return errors + [f"cannot inspect subject refs in archive: {exc}"]
    corpus = "\n".join(text_parts)
    for required_sha in suite["required_subject_shas"]:
        if required_sha.lower() not in corpus and required_sha[:8].lower() not in corpus:
            errors.append(f"artifact does not identify pinned subject ref {required_sha}")
    return errors


def audit_extended_run(root: Path, suite: dict, rep: int, ordinal: int,
                       lane_ports: list[int]) -> tuple[dict, list[str], list[str]]:
    name = expected_run_name(suite["id"], rep)
    run_dir = root / "logs" / name
    record, errors, warnings = audit_run(run_dir, False, False)
    record.update({"suite": suite["id"], "replicate": rep, "ordinal": ordinal})
    label = read_json(run_dir / "label.json") or {}
    if record.get("terminal_label"):
        if record["terminal_label"] == "dependency-failure":
            expected_source = expected_run_name(suite["input_from"], rep)
            if label.get("source_run") != expected_source:
                errors.append(
                    f"dependency-failure source {label.get('source_run')!r} != {expected_source!r}"
                )
        return record, errors, warnings

    receipt = read_json(run_dir / "receipt.json") or {}
    task = receipt.get("task") or {}
    if task.get("sha256") != suite["current_task_sha256"]:
        errors.append("task hash differs from pinned extended matrix")
    runtime = ((receipt.get("sandbox") or {}).get("runtime") or {})
    if runtime.get("require_git_tag") is not True:
        errors.append("extended run did not require a git tag")
    expected_port = lane_ports[ordinal % len(lane_ports)]
    endpoint = ((receipt.get("vllm") or {}).get("api_url") or "")
    if f":{expected_port}/" not in endpoint:
        errors.append(f"run endpoint does not match deterministic lane port {expected_port}")
    if suite.get("input_from"):
        expected_source = expected_run_name(suite["input_from"], rep)
        mounted = str(runtime.get("input_mount") or "")
        if not mounted.endswith(f"tooling/workspace/{expected_source}"):
            errors.append(f"board input mount does not derive from {expected_source}")
    if suite.get("input_path"):
        mounted = str(runtime.get("input_mount") or "")
        if Path(mounted) != Path(suite["input_path"]):
            errors.append("frozen-fixture input path mismatch")
    if suite.get("subject_pin"):
        errors.extend(audit_subject_refs(root, suite, run_dir))
    return record, errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--matrix", type=Path,
        default=Path(__file__).with_name("gemma4-31b-q4-extended-matrix.json"),
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    matrix_path = args.matrix.resolve()
    matrix = json.loads(matrix_path.read_text())
    lane_ports = [int(port) for port in matrix["lane_ports"]]
    records = []
    errors = []
    warnings = []
    ordinal = 0
    for suite in matrix["suites"]:
        if suite["id"] not in RUN_PREFIXES:
            errors.append(f"unknown suite id in matrix: {suite['id']}")
            continue
        for rep in range(1, int(matrix["replicates"]) + 1):
            record, run_errors, run_warnings = audit_extended_run(
                root, suite, rep, ordinal, lane_ports,
            )
            records.append(record)
            name = record["run_name"]
            errors.extend(f"{name}: {message}" for message in run_errors)
            warnings.extend(f"{name}: {message}" for message in run_warnings)
            ordinal += 1

    invalid = []
    invalid_root = root / "logs" / "_infra_invalid"
    if invalid_root.is_dir():
        for attempt in sorted(path for path in invalid_root.iterdir() if path.is_dir()):
            files = {}
            for path in sorted(candidate for candidate in attempt.rglob("*") if candidate.is_file()):
                files[str(path.relative_to(attempt))] = {
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            invalid.append({"attempt": attempt.name, "files": files})

    expected = len(matrix["suites"]) * int(matrix["replicates"])
    document = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "matrix": {
            "path": str(matrix_path),
            "sha256": sha256(matrix_path),
        },
        "expected_runs": expected,
        "audited_runs": len(records),
        "passed": len(records) == expected and not errors,
        "errors": errors,
        "warnings": warnings,
        "runs": records,
        "preserved_infrastructure_invalid_attempts": invalid,
        "scope_note": (
            "This audit proves identity, configuration, routing, telemetry, and artifact "
            "preservation. Suite-specific substantive grading and visual/workbook/code "
            "inspection are separate required overlays; this document is not a quality pass."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps({
        "passed": document["passed"], "runs": len(records),
        "errors": len(errors), "warnings": len(warnings),
        "invalid_attempts": len(invalid),
    }, sort_keys=True))
    raise SystemExit(0 if document["passed"] else 1)


if __name__ == "__main__":
    main()
