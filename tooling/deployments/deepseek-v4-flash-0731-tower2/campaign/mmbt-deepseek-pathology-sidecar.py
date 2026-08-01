#!/usr/bin/env python3
"""Attach deterministic MMBT taxonomy labels to unambiguous terminations.

This intentionally does not classify ``model_stopped`` or generic
stuck-detector outcomes: distinguishing floor failure, partial output,
scaffold-and-stop, and stuck-in-research requires inspecting the workspace and
transcript. Existing labels are never overwritten.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path


LOG_ROOTS = (
    Path("/home/michael/bench-deepseek-v4-flash-0731/logs"),
    Path("/home/michael/bench-deepseek-v4-flash-extended/logs"),
)
MICRO_STATUS = Path("/tmp/bench-autopilot/status.json")
EXTENDED_STATUS = Path("/tmp/mmbt-deepseek-v4-flash-extended/status.json")
EVENT_LOG = Path("/tmp/bench-autopilot/pathology-sidecar.log")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def classification(reason: str):
    if reason.startswith("model_exceeded_max_tokens_"):
        return (
            "runaway-generation",
            [],
            "A single model response reached the harness max-output-token budget without a terminal tool call.",
        )
    if reason == "api_error: timed out" or reason.startswith("api_error: timed out"):
        return (
            "timeout",
            [],
            "The harness's per-call HTTP timeout fired; MMBT treats this as a model outcome, not disposable infrastructure noise.",
        )
    if reason.startswith("api_error:"):
        return (
            "api-error",
            [],
            "The serving API returned an error during the model loop; MMBT retains this terminal outcome.",
        )
    if reason.startswith("endpoint_"):
        return None  # supervisor-classified infrastructure; eligible for retry
    return None


def label_new_outcomes() -> int:
    written = 0
    for root in LOG_ROOTS:
        if not root.is_dir():
            continue
        for run_dir in sorted(path for path in root.iterdir() if path.is_dir() and not path.name.startswith("_")):
            summary_path = run_dir / "summary.json"
            label_path = run_dir / "label.json"
            if not summary_path.exists() or label_path.exists():
                continue
            summary = read_json(summary_path)
            reason = str(summary.get("finish_reason") or "")
            match = classification(reason)
            if not match:
                continue
            primary, sub_labels, notes = match
            doc = {
                "primary": primary,
                "sub_labels": sub_labels,
                "notes": notes,
                "labeler": "deterministic-taxonomy-sidecar",
                "labeled_at": datetime.now(timezone.utc).isoformat(),
                "evidence": {
                    "summary_finish_reason": reason,
                    "summary_elapsed_s": summary.get("elapsed_s"),
                    "summary_iterations": summary.get("iterations"),
                    "summary_completion_tokens": summary.get("total_completion_tokens"),
                },
            }
            temporary = label_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(doc, indent=2) + "\n")
            temporary.replace(label_path)
            EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
            with EVENT_LOG.open("a") as handle:
                handle.write(f"{doc['labeled_at']} {run_dir.name} {primary} {reason}\n")
            written += 1
    return written


def campaign_complete() -> bool:
    micro = read_json(MICRO_STATUS)
    extended = read_json(EXTENDED_STATUS)
    return (
        micro.get("phase") == "COMPLETE"
        and micro.get("grand_done") == micro.get("grand_total") == 36
        and extended.get("phase") == "COMPLETE"
        and extended.get("done") == extended.get("total") == 12
    )


def main() -> None:
    while True:
        label_new_outcomes()
        if campaign_complete():
            return
        time.sleep(60)


if __name__ == "__main__":
    main()
