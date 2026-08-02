#!/usr/bin/env python3
"""Fail-closed audit of Gemma canonical evidence and preserved attempts."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


TASKS = [
    "p1_bugfix", "p1_testwrite", "p1_refactor", "p2_extract", "p2_ci",
    "p2_hallucination", "p2_triage", "p3_doc", "p3_business",
    "p3_market", "p3_writing", "p3_pm",
]
MODEL = "Gemma-4-31B-it-QAT-Q4_0"
MODEL_SHA = "179cfb99212709597eae5929112cfca677e1bbf566178b479ae1da0c4772874b"
SERVER_SHA = "200b403b5735418ff1f6da0cea1938e413e11869ae362e8044a12b0df04622fc"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def parse_supplement_mappings(values: list[str]) -> tuple[dict[str, str], list[str]]:
    mappings = {}
    errors = []
    for value in values:
        original, separator, supplemental = value.partition("=")
        if not separator or not original or not supplemental:
            errors.append(
                f"invalid pretelemetry supplement mapping {value!r}; "
                "expected CANONICAL_RUN=SUPPLEMENTAL_RUN"
            )
            continue
        if original in mappings:
            errors.append(f"duplicate pretelemetry supplement mapping for {original}")
            continue
        mappings[original] = supplemental
    return mappings, errors


def default_root(script_path: Path) -> Path:
    """Resolve the repository root for a script installed directly in tooling/."""
    return script_path.resolve().parents[1]


def audit_invalid_attempts(
    invalid_root: Path, classification_path: Path, label: str,
) -> tuple[list[dict], dict | None, list[str]]:
    """Inventory excluded attempts and prove every exclusion is classified."""
    errors: list[str] = []
    attempts = sorted(
        attempt for attempt in invalid_root.glob(f"*{label}*")
        if attempt.is_dir()
    ) if invalid_root.is_dir() else []
    if not attempts:
        return [], None, errors

    document = read_json(classification_path)
    if not isinstance(document, dict):
        return [], None, [f"invalid-attempt classification document missing or invalid: {classification_path}"]
    entries = document.get("attempts")
    if not isinstance(entries, dict):
        return [], None, ["invalid-attempt classification document lacks attempts object"]

    records = []
    observed_names = {attempt.name for attempt in attempts}
    extra_names = sorted(set(entries) - observed_names)
    if extra_names:
        errors.append(f"classified invalid attempts missing from evidence tree: {extra_names}")

    for attempt in attempts:
        entry = entries.get(attempt.name)
        evidence = {}
        for path in sorted(path for path in attempt.rglob("*") if path.is_file()):
            evidence[str(path.relative_to(attempt))] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        if not isinstance(entry, dict):
            errors.append(f"{attempt.name}: missing invalid-attempt classification")
            records.append({"attempt": attempt.name, "files": evidence})
            continue

        source_run = entry.get("source_run")
        if not isinstance(source_run, str) or not attempt.name.startswith(source_run):
            errors.append(f"{attempt.name}: classification source_run does not match attempt")
        if entry.get("classification") != "infrastructure-invalid":
            errors.append(f"{attempt.name}: exclusion is not classified infrastructure-invalid")
        if entry.get("classified_before_grade") is not True:
            errors.append(f"{attempt.name}: exclusion was not classified before grading")
        if not entry.get("reason_code"):
            errors.append(f"{attempt.name}: classification lacks reason_code")
        affirmative = entry.get("affirmative_evidence")
        if not isinstance(affirmative, list) or not affirmative:
            errors.append(f"{attempt.name}: classification lacks affirmative evidence")
        replacement = entry.get("replacement") or {}
        if replacement.get("required") is not True or replacement.get("status") != "completed":
            errors.append(f"{attempt.name}: exact canonical replacement is not completed")
        incident = classification_path.parent / str(entry.get("incident_document") or "")
        if not incident.is_file():
            errors.append(f"{attempt.name}: incident document is missing")

        expected_files = entry.get("expected_files") or {}
        if not isinstance(expected_files, dict) or not expected_files:
            errors.append(f"{attempt.name}: classification lacks expected file hashes")
        else:
            for relative, expected_hash in sorted(expected_files.items()):
                observed = evidence.get(relative)
                if observed is None:
                    errors.append(f"{attempt.name}: classified evidence missing {relative}")
                elif observed["sha256"] != expected_hash:
                    errors.append(f"{attempt.name}: classified evidence hash mismatch for {relative}")

        records.append({
            "attempt": attempt.name,
            "classification": entry,
            "files": evidence,
        })

    classification_record = {
        "path": str(classification_path.resolve()),
        "bytes": classification_path.stat().st_size,
        "sha256": sha256(classification_path),
    }
    return records, classification_record, errors


def audit_replacement_controls(logs: Path, invalid_records: list[dict]) -> list[str]:
    """Prove defect-specific controls on exact canonical replacements."""
    errors: list[str] = []
    for record in invalid_records:
        entry = record.get("classification") or {}
        replacement = entry.get("replacement") or {}
        run_name = replacement.get("canonical_run")
        if not run_name:
            continue
        run_dir = logs / run_name
        if not (run_dir / "summary.json").is_file() or not (
            run_dir / "workspace_final.tar.gz"
        ).is_file():
            errors.append(f"{record['attempt']}: exact replacement evidence is incomplete")
            continue
        if entry.get("reason_code") != "server-transport-timeout-below-native-envelope":
            continue
        receipt = read_json(run_dir / "receipt.json") or {}
        processes = (receipt.get("serving") or {}).get("host_processes") or []
        timeouts = []
        for process in processes:
            argv = process.get("argv") or []
            for index, value in enumerate(argv[:-1]):
                if value == "--timeout":
                    try:
                        timeouts.append(int(argv[index + 1]))
                    except (TypeError, ValueError):
                        pass
        if not timeouts or min(timeouts) < 14400:
            errors.append(
                f"{record['attempt']}: replacement does not prove a >=14400-second server timeout"
            )
        summary = read_json(run_dir / "summary.json") or {}
        if "timed out" in str(summary.get("finish_reason") or "").lower():
            errors.append(f"{record['attempt']}: replacement also ended in a transport timeout")
    return errors


def audit_run(run_dir: Path, allow_pretelemetry: bool, require_grades: bool) -> tuple[dict, list[str], list[str]]:
    name = run_dir.name
    errors: list[str] = []
    warnings: list[str] = []
    files = {}
    for filename in (
        "receipt.json", "transcript.jsonl", "summary.json", "workspace_final.tar.gz",
        "cost.json", "gpu_telemetry.json", "grade.json", "label.json",
    ):
        path = run_dir / filename
        if path.is_file():
            files[filename] = {"bytes": path.stat().st_size, "sha256": sha256(path)}

    label = read_json(run_dir / "label.json")
    summary = read_json(run_dir / "summary.json")
    terminal_label = bool(label and label.get("primary"))
    completed = bool(summary and (run_dir / "workspace_final.tar.gz").is_file())
    terminal_only = terminal_label and not completed
    if not completed and not terminal_label:
        errors.append("not a completed run or explicit terminal label")
        return {"run_name": name, "files": files}, errors, warnings
    if terminal_only:
        primary = label.get("primary")
        if primary == "dependency-failure":
            if not label.get("source_run") or not label.get("source_primary"):
                errors.append("dependency-failure label lacks source evidence")
            return {
                "run_name": name, "outcome_kind": "dependency-failure",
                "terminal_label": primary, "files": files,
            }, errors, warnings

    required_files = ["receipt.json", "transcript.jsonl", "cost.json"]
    if completed:
        required_files.extend(["summary.json", "workspace_final.tar.gz"])
    for required in required_files:
        if required not in files:
            prefix = "terminal outcome missing preserved " if terminal_only else "missing "
            errors.append(f"{prefix}{required}")
    if require_grades and not terminal_only and "grade.json" not in files:
        errors.append("missing grade.json")
    if "gpu_telemetry.json" not in files:
        if allow_pretelemetry and not terminal_only:
            warnings.append("pre-telemetry valid attempt; supplemental telemetry required")
        else:
            prefix = "terminal outcome missing preserved " if terminal_only else "missing "
            errors.append(f"{prefix}gpu_telemetry.json")
    if terminal_only and any(
        required not in files
        for required in ("receipt.json", "transcript.jsonl", "cost.json", "gpu_telemetry.json")
    ):
        return {
            "run_name": name, "outcome_kind": "terminal-label",
            "terminal_label": label.get("primary"), "files": files,
        }, errors, warnings

    receipt = read_json(run_dir / "receipt.json") or {}
    defaults = receipt.get("inference_request_defaults") or {}
    if (receipt.get("harness") or {}).get("git_dirty") is not False:
        errors.append("receipt reports dirty harness worktree")
    if (receipt.get("vllm") or {}).get("served_model_name") != MODEL:
        errors.append("wrong served model in receipt")
    expected_defaults = {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 64,
        "max_model_len": 262144,
        "max_output_tokens_cap": 262144,
    }
    for key, expected in expected_defaults.items():
        if defaults.get(key) != expected:
            errors.append(f"wrong {key}: {defaults.get(key)!r}")
    manifest = ((receipt.get("serving") or {}).get("manifest") or {}).get("payload") or {}
    if ((manifest.get("artifact") or {}).get("sha256")) != MODEL_SHA:
        errors.append("serving manifest model hash mismatch")
    processes = (receipt.get("serving") or {}).get("host_processes") or []
    if not processes or any(process.get("exe_sha256") != SERVER_SHA for process in processes):
        errors.append("host llama-server provenance mismatch")
    models = (((receipt.get("serving") or {}).get("endpoint_models") or {}).get("payload") or {}).get("data") or []
    if [model.get("id") for model in models] != [MODEL]:
        errors.append("live /v1/models identity mismatch")
    hardware = (receipt.get("hardware") or {}).get("nvidia_smi") or []
    if len(hardware) != 2 or any("500.00 W" not in row for row in hardware):
        errors.append("receipt does not prove two 500 W GPU limits")
    if summary and summary.get("model") != MODEL:
        errors.append("summary model mismatch")

    transcript_path = run_dir / "transcript.jsonl"
    transcript = []
    try:
        transcript = [json.loads(line) for line in transcript_path.read_text().splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError):
        errors.append("transcript is not valid JSONL")
    model_turns = [row for row in transcript if row.get("type") == "model"]
    if not model_turns:
        errors.append("transcript has no model turns")

    cost = read_json(run_dir / "cost.json")
    if "cost.json" in files:
        if not isinstance(cost, dict):
            errors.append("cost.json is not valid JSON")
            cost = {}
        else:
            if cost.get("run_name") != name:
                errors.append("cost run name mismatch")
            if cost.get("model") != MODEL:
                errors.append("cost model mismatch")
            if not isinstance(cost.get("wall_s"), (int, float)) or cost.get("wall_s") <= 0:
                errors.append("cost wall_s is not positive")

    telemetry = read_json(run_dir / "gpu_telemetry.json")
    telemetry_summary = None
    if telemetry:
        observed = (telemetry.get("attribution") or {}).get("active_gpu_ids_observed") or []
        coverage = (telemetry.get("sampling") or {}).get("coverage_fraction_of_wall")
        cap = (telemetry.get("active_gpu") or {}).get("configured_cap_w")
        if len(observed) != 1 or observed[0] not in ("0", "1"):
            errors.append("telemetry does not identify exactly one replica GPU")
        if cap != 500.0:
            errors.append("telemetry cap is not 500 W")
        if terminal_only and not (telemetry.get("sampling") or {}).get("window_source"):
            errors.append("terminal telemetry lacks an explicit evidence window source")
        if not isinstance(coverage, (int, float)) or coverage < 0.80:
            warnings.append(f"telemetry coverage below 80%: {coverage!r}")
        telemetry_summary = {
            "gpu": observed,
            "coverage": coverage,
            "mean_power_w": (telemetry.get("active_gpu") or {}).get("mean_power_w"),
            "mean_sm_util_pct": (telemetry.get("active_gpu") or {}).get("mean_sm_util_pct"),
            "max_temp_c": (telemetry.get("active_gpu") or {}).get("max_temp_c"),
            "cpu_package_mean_power_w": (telemetry.get("cpu_package_shared_context") or {}).get("mean_power_w"),
        }

    grade = read_json(run_dir / "grade.json")
    summary_doc = summary or {}
    return {
        "run_name": name,
        "outcome_kind": "terminal-label" if terminal_only else "completed-workspace",
        "terminal_label": label.get("primary") if terminal_only else None,
        "harness_git_sha": (receipt.get("harness") or {}).get("git_sha"),
        "endpoint": (receipt.get("vllm") or {}).get("api_url"),
        "finish_reason": summary_doc.get("finish_reason") or (
            f"terminal:{label.get('primary')}" if terminal_only else None
        ),
        "elapsed_s": summary_doc.get("elapsed_s") or (cost or {}).get("wall_s"),
        "iterations": summary_doc.get("iterations") or (cost or {}).get("iters"),
        "completion_tokens": summary_doc.get("total_completion_tokens") or (
            ((cost or {}).get("tokens") or {}).get("completion_total")
        ),
        "prompt_tokens_cumulative": summary_doc.get("total_prompt_tokens") or (
            ((cost or {}).get("tokens") or {}).get("prompt_total")
        ),
        "model_turns": len(model_turns),
        "length_finishes": sum(row.get("finish_reason") == "length" for row in model_turns),
        "grade_verdict": grade.get("verdict") if grade else None,
        "telemetry": telemetry_summary,
        "files": files,
    }, errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=default_root(Path(__file__)))
    parser.add_argument("--label", default="gemma4-31b-q4")
    parser.add_argument("--target-n", type=int, default=3)
    parser.add_argument("--allow-pretelemetry-run", action="append", default=[])
    parser.add_argument(
        "--pretelemetry-supplement", action="append", default=[],
        metavar="CANONICAL_RUN=SUPPLEMENTAL_RUN",
    )
    parser.add_argument("--require-grades", action="store_true")
    parser.add_argument(
        "--invalid-classifications", type=Path,
        default=None,
        help="classification ledger for preserved infrastructure-invalid attempts",
    )
    parser.add_argument("--raw-telemetry", type=Path, default=Path("/home/michael/gemma4-campaign-state/telemetry/gemma4-31b-q4-gpu.csv"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    logs = root / "logs"
    allowed = set(args.allow_pretelemetry_run)
    supplements, mapping_errors = parse_supplement_mappings(args.pretelemetry_supplement)
    records = []
    errors = list(mapping_errors)
    warnings = []
    for task in TASKS:
        for rep in range(1, args.target_n + 1):
            name = f"{task}_{args.label}_v{rep}"
            record, run_errors, run_warnings = audit_run(logs / name, name in allowed, args.require_grades)
            records.append(record)
            errors.extend(f"{name}: {message}" for message in run_errors)
            warnings.extend(f"{name}: {message}" for message in run_warnings)

    missing_mappings = sorted(allowed - set(supplements))
    extra_mappings = sorted(set(supplements) - allowed)
    errors.extend(
        f"{name}: allowed pre-telemetry run has no audited supplemental mapping"
        for name in missing_mappings
    )
    errors.extend(
        f"{name}: supplemental mapping supplied without --allow-pretelemetry-run"
        for name in extra_mappings
    )
    supplemental_records = []
    for original, supplemental in sorted(supplements.items()):
        record, run_errors, run_warnings = audit_run(
            logs / supplemental, allow_pretelemetry=False, require_grades=False,
        )
        record["supplements_run"] = original
        supplemental_records.append(record)
        errors.extend(f"{supplemental}: {message}" for message in run_errors)
        warnings.extend(f"{supplemental}: {message}" for message in run_warnings)

    invalid_root = logs / "_invalid"
    classification_path = args.invalid_classifications or (
        root / "tooling" / "deployments" / "gemma4-31b-q4-tower2" /
        "invalid-attempt-classifications.json"
    )
    invalid, invalid_classification_record, invalid_errors = audit_invalid_attempts(
        invalid_root, classification_path, args.label,
    )
    errors.extend(invalid_errors)
    errors.extend(audit_replacement_controls(logs, invalid))

    raw = None
    if args.raw_telemetry.is_file():
        with args.raw_telemetry.open("rb") as handle:
            lines = sum(1 for _ in handle)
        raw = {
            "path": str(args.raw_telemetry.resolve()),
            "bytes": args.raw_telemetry.stat().st_size,
            "lines": lines,
            "sha256_at_audit_time": sha256(args.raw_telemetry),
        }
    else:
        errors.append(f"raw telemetry missing: {args.raw_telemetry}")

    document = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "label": args.label,
        "target_n": args.target_n,
        "expected_runs": len(TASKS) * args.target_n,
        "audited_runs": len(records),
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "raw_telemetry": raw,
        "runs": records,
        "pretelemetry_supplements": supplemental_records,
        "invalid_attempt_classifications": invalid_classification_record,
        "preserved_invalid_attempts": invalid,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps({
        "passed": document["passed"], "runs": len(records),
        "errors": len(errors), "warnings": len(warnings), "invalid_attempts": len(invalid),
    }, sort_keys=True))
    raise SystemExit(0 if document["passed"] else 1)


if __name__ == "__main__":
    main()
