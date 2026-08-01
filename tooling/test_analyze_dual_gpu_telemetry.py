#!/usr/bin/env python3
import importlib.util
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).with_name("analyze_dual_gpu_telemetry.py")
SPEC = importlib.util.spec_from_file_location("telemetry_analyzer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def point(second: int, cell: str = "cell-v1") -> dict:
    ts = datetime(2026, 1, 1, 0, 0, second, tzinfo=timezone.utc).timestamp()
    gpu = {
        "0": {"power_w": 40.0, "util_sm": 95.0, "util_mem": 1.0,
              "mem_used_mib": 10.0, "temp_c": 50.0, "sm_clk_mhz": 1000.0},
        "1": {"power_w": 60.0, "util_sm": 95.0, "util_mem": 1.0,
              "mem_used_mib": 10.0, "temp_c": 51.0, "sm_clk_mhz": 1000.0},
    }
    return {"ts": ts, "cell": cell, "gpu": gpu, "combined_power_w": 100.0}


def main() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        run_dir = root / "cell-v1"
        run_dir.mkdir()
        (run_dir / "summary.json").write_text(json.dumps({
            "started_at": "2026-01-01T00:00:02+00:00",
            "ended_at": "2026-01-01T00:00:18+00:00",
            "elapsed_s": 16.0,
        }))
        points = [point(second) for second in (0, 5, 10, 15, 20, 25)]
        report = MODULE.analyze(points, [root], root / "power.csv", 600.0, 0.13, 15.0)
        doc = report["cell-v1"]
        sampling = doc["sampling"]
        assert doc["schema_version"] == 2
        assert sampling["paired_samples"] == 3
        assert sampling["paired_samples_before_window_clip"] == 6
        assert sampling["excluded_before_run"] == 1
        assert sampling["excluded_after_run"] == 2
        assert sampling["integrated_coverage_s"] == 13.0
        assert sampling["coverage_fraction_of_wall"] == 0.8125
        assert sampling["first_sample"].endswith("00:00:05+00:00")
        assert sampling["last_sample"].endswith("00:00:15+00:00")
        assert doc["energy_and_cost"]["sampled_kwh"] == 0.000361
        assert doc["combined"]["time_weighted_power_w"] == 100.0
        print(json.dumps({
            "coverage_s": sampling["integrated_coverage_s"],
            "paired_samples": sampling["paired_samples"],
            "sampled_kwh": doc["energy_and_cost"]["sampled_kwh"],
        }, sort_keys=True))


if __name__ == "__main__":
    main()
