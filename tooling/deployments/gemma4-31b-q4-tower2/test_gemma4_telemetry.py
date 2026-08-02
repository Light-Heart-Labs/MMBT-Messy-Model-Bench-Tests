#!/usr/bin/env python3
import csv
import importlib.util
import json
from pathlib import Path


DEPLOY = Path(__file__).parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, DEPLOY / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LOGGER = load("gemma4_gpu_telemetry", "gemma4_gpu_telemetry.py")
ANALYZER = load("analyze_replica_telemetry", "analyze_replica_telemetry.py")


def test_rapl_power_handles_counter_wrap():
    power, state = LOGGER.rapl_power((990, 10.0), 20, 12.0, 1000)
    assert power == 30 / 1_000_000 / 2
    assert state == (20, 12.0)


def test_replica_analyzer_attributes_only_the_active_lane(tmp_path):
    logs = tmp_path / "logs"
    run = logs / "p2_extract_gemma4-31b-q4_v1"
    run.mkdir(parents=True)
    (run / "summary.json").write_text(json.dumps({
        "started_at": "2026-08-02T00:00:00+00:00",
        "ended_at": "2026-08-02T00:00:10+00:00",
        "elapsed_s": 10,
    }))
    csv_path = tmp_path / "gpu.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(LOGGER.FIELDS)
        for second in (0, 5, 10):
            ts = f"2026-08-02T00:00:{second:02d}Z"
            writer.writerow([ts, 0, 8000, 500, 400, 95, 20, 65000, 70, 2700,
                             run.name, 123, 100])
            writer.writerow([ts, 1, 8001, 500, 300, 80, 15, 65000, 65, 2600,
                             "other_cell", 456, 100])
    report = ANALYZER.analyze(csv_path, [logs], 500, 0.13, 15)
    doc = report[run.name]
    assert doc["attribution"]["active_gpu_ids_observed"] == ["0"]
    assert doc["active_gpu"]["mean_power_w"] == 400
    assert doc["sampling"]["coverage_fraction_of_wall"] == 1.0
    assert doc["concurrency"]["other_gpu_cell_sample_counts"] == {"other_cell": 3}
    assert doc["concurrency"]["mean_observed_two_gpu_plus_cpu_package_w"] == 800
    assert doc["sampling"]["window_source"] == "summary.json"


def test_replica_analyzer_uses_preserved_terminal_outcome_window(tmp_path):
    logs = tmp_path / "logs"
    run = logs / "p3_market_gemma4-31b-q4_v1"
    run.mkdir(parents=True)
    (run / "receipt.json").write_text(json.dumps({
        "captured_at": "2026-08-02T00:00:00+00:00",
    }))
    (run / "label.json").write_text(json.dumps({
        "primary": "identical-call-loop",
        "labeled_at": "2026-08-02T00:00:10+00:00",
    }))
    (run / "transcript.jsonl").write_text("\n".join([
        json.dumps({"t": "2026-08-02T00:00:02+00:00", "type": "model"}),
        json.dumps({"t": "2026-08-02T00:00:08+00:00", "type": "tool"}),
    ]) + "\n")
    csv_path = tmp_path / "gpu.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(LOGGER.FIELDS)
        for second in (0, 5, 10):
            ts = f"2026-08-02T00:00:{second:02d}Z"
            writer.writerow([ts, 1, 8001, 500, 450, 96, 20, 65000, 75, 2700,
                             run.name, 456, 110])
    report = ANALYZER.analyze(csv_path, [logs], 500, 0.13, 15)
    doc = report[run.name]
    assert doc["sampling"]["window_source"] == (
        "receipt.json:captured_at..label.json:labeled_at"
    )
    assert doc["sampling"]["window_wall_s"] == 10.0
    assert doc["sampling"]["coverage_fraction_of_wall"] == 1.0
    assert doc["attribution"]["active_gpu_ids_observed"] == ["1"]
