#!/usr/bin/env python3
from pathlib import Path


SCRIPT = Path(__file__).with_name("snapshot_gemma4_telemetry.sh").read_text()


def test_snapshot_requires_a_clean_boundary_and_refuses_overwrite():
    assert "benchmark work is active" in SCRIPT
    assert "refusing to overwrite telemetry snapshot" in SCRIPT
    assert "snapshot destination must be an absolute CSV" in SCRIPT


def test_snapshot_pauses_writer_validates_csv_and_restores_services():
    assert 'systemctl --user stop "$SIDECAR" "$LOGGER"' in SCRIPT
    assert "telemetry snapshot does not end at a complete line" in SCRIPT
    assert "telemetry snapshot header drift" in SCRIPT
    assert "trap restart_services EXIT" in SCRIPT
    assert "sha256sum" in SCRIPT
