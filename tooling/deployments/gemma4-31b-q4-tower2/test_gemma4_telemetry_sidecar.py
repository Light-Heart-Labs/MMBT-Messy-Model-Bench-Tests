#!/usr/bin/env python3
from pathlib import Path


SCRIPT = Path(__file__).with_name("gemma4-telemetry-sidecar.sh").read_text()


def test_sidecar_derives_cost_for_completed_and_terminal_outcomes():
    assert "-name summary.json -o -name label.json" in SCRIPT
    assert '[[ -f "$run_dir/receipt.json" && -f "$run_dir/transcript.jsonl" ]]' in SCRIPT
    assert "-printf '%h\\n' | sort -u" in SCRIPT
    assert 'extract_cost.py" "$run_dir"' in SCRIPT


def test_sidecar_writes_per_run_telemetry_artifacts():
    assert "--write-run-artifacts" in SCRIPT
    assert "--cap-per-gpu 500" in SCRIPT
