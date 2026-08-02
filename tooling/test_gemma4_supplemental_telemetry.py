#!/usr/bin/env python3
from pathlib import Path


SCRIPT = Path(__file__).with_name("run_gemma4_supplemental_telemetry.sh").read_text()


def test_supplements_use_distinct_noncanonical_label_and_exact_shards():
    assert 'LABEL="gemma4-31b-q4-telemetry-supplement"' in SCRIPT
    assert "BENCH_LANE_COUNT=24" in SCRIPT
    assert "BENCH_LANE_INDEX=0" in SCRIPT
    assert "BENCH_LANE_INDEX=1" in SCRIPT
    assert '"$LABEL" 2' in SCRIPT


def test_supplements_fail_closed_on_campaign_overlap_and_power_drift():
    assert "mmbt-gemma4-canonical-n3-r3.service" in SCRIPT
    assert "another benchmark harness is active" in SCRIPT
    assert '"500.00 500.00"' in SCRIPT
    assert "will not be overwritten" in SCRIPT


def test_supplements_require_telemetry_before_success():
    assert "gpu_telemetry.json" in SCRIPT
    assert "SUPPLEMENTAL_TELEMETRY_COMPLETE" in SCRIPT


def test_supplements_require_idle_replica_slots_at_launch():
    assert 'http://127.0.0.1:${port}/slots' in SCRIPT
    assert "all(.[]; .is_processing == false)" in SCRIPT
    assert "retry at an idle boundary" in SCRIPT
