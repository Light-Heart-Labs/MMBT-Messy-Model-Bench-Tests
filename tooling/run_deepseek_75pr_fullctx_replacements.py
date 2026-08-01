#!/usr/bin/env python3
"""Produce three valid frozen-75PR outcomes without an artificial output cap.

Existing runs are never overwritten. A completed run is excluded only when it
actually terminated at a per-request cap smaller than the served context. Runs
that complete normally below an older cap remain valid because their outcome
was not constrained. Replacement runs use the full served context as their cap;
the harness's dynamic 14K safety reserve remains authoritative.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


TOOLING = Path(__file__).resolve().parent
ROOT = TOOLING.parent
sys.path.insert(0, str(TOOLING))

import run_deepseek_extended_suites as runner  # noqa: E402


PREFIX = "deepseek-v4-flash-0731_75pr_v"
AUDIT_DIR = runner.LOGS / "_campaign_audit"
MANIFEST = AUDIT_DIR / "75pr-valid-replicates.json"
TARGET_VALID = 3
MAX_NEW_RUNS = 4


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def classify(rep: int, served_context: int) -> dict:
    name = f"{PREFIX}{rep}"
    log_dir = runner.LOGS / name
    summary = load_json(log_dir / "summary.json")
    label = load_json(log_dir / "label.json")
    receipt = load_json(log_dir / "receipt.json")
    finish_reason = str(summary.get("finish_reason") or "")
    configured_cap = (
        receipt.get("inference_request_defaults", {}).get("max_output_tokens_cap")
    )
    complete = runner.completed(log_dir)
    constrained = (
        complete
        and finish_reason.startswith("model_exceeded_max_tokens_")
        and isinstance(configured_cap, int)
        and configured_cap < served_context
    )
    if not complete:
        disposition = "incomplete"
    elif constrained:
        disposition = "excluded_artificial_output_cap"
    elif runner.infra_invalid(log_dir):
        disposition = "excluded_infrastructure_invalid"
    else:
        disposition = "valid"
    return {
        "rep": rep,
        "run": name,
        "disposition": disposition,
        "finish_reason": finish_reason or None,
        "terminal_label": label.get("primary"),
        "configured_output_cap": configured_cap,
        "served_context": served_context,
        "summary_present": bool(summary),
        "archive_present": (log_dir / "workspace_final.tar.gz").is_file(),
        "receipt_present": bool(receipt),
    }


def existing_reps() -> list[int]:
    found = []
    pattern = re.compile(rf"^{re.escape(PREFIX)}(\d+)$")
    for path in runner.LOGS.glob(f"{PREFIX}*"):
        match = pattern.match(path.name)
        if match:
            found.append(int(match.group(1)))
    return sorted(set(found))


def write_manifest(rows: list[dict], served_context: int, status: str) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    valid = [row for row in rows if row["disposition"] == "valid"]
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaign": "DeepSeek-V4-Flash-0731 frozen 75-PR N=3",
        "policy": (
            "Preserve every run; exclude only runs terminated by a configured "
            "per-request cap below the served context, then add full-context "
            "replacement replicates until three valid outcomes exist."
        ),
        "served_context": served_context,
        "full_context_output_cap": served_context,
        "dynamic_safety_reserve": 14000,
        "target_valid_replicates": TARGET_VALID,
        "valid_replicates": len(valid),
        "valid_run_names": [row["run"] for row in valid[:TARGET_VALID]],
        "status": status,
        "runs": rows,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    audit_only = "--audit-only" in sys.argv[1:]
    matrix = load_json(runner.MATRIX_PATH)
    runner.validate_matrix(matrix)
    served_context = int(matrix["served_context_tokens"])
    suite = next(
        item for item in matrix["suites"]
        if item["id"] == "dreamserver-75-pr-audit"
    )
    if int(suite["max_output_tokens_cap"]) != served_context:
        raise RuntimeError("75-PR output cap must equal the served context")

    rows = [classify(rep, served_context) for rep in existing_reps()]
    valid = [row for row in rows if row["disposition"] == "valid"]
    write_manifest(rows, served_context, "running" if len(valid) < TARGET_VALID else "complete")
    if audit_only:
        print(
            json.dumps(
                {
                    "valid": [row["run"] for row in valid],
                    "excluded": [
                        row for row in rows if row["disposition"].startswith("excluded_")
                    ],
                    "manifest": str(MANIFEST),
                },
                indent=2,
            )
        )
        return
    runner.write_status(
        phase="FULLCTX_REPLACEMENTS_STARTING",
        valid_75pr=len(valid),
        target_75pr=TARGET_VALID,
        manifest=str(MANIFEST),
    )

    new_runs = 0
    next_rep = max(existing_reps() or [0]) + 1
    while len(valid) < TARGET_VALID:
        if new_runs >= MAX_NEW_RUNS:
            write_manifest(rows, served_context, "replacement_limit_reached")
            raise RuntimeError("full-context replacement limit reached")
        runner.supervise_one(
            suite,
            next_rep,
            served_context,
            float(matrix["top_p"]),
        )
        new_runs += 1
        rows = [classify(rep, served_context) for rep in existing_reps()]
        valid = [row for row in rows if row["disposition"] == "valid"]
        write_manifest(rows, served_context, "running" if len(valid) < TARGET_VALID else "complete")
        next_rep = max(existing_reps()) + 1

    # Retain the original 12/12 matrix completion fields so campaign sidecars
    # make one final artifact pass and then exit normally. The replacement
    # details and authoritative valid-run set remain explicit in this status
    # object and the preserved manifest.
    runner.write_status(
        phase="COMPLETE",
        done=12,
        total=12,
        valid_75pr=len(valid),
        target_75pr=TARGET_VALID,
        manifest=str(MANIFEST),
    )
    runner.event(
        "fullctx_75pr_replacements_complete",
        valid=len(valid),
        target=TARGET_VALID,
        manifest=str(MANIFEST),
    )


if __name__ == "__main__":
    main()
