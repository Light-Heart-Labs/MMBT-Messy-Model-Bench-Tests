#!/usr/bin/env python3
"""Regression checks for saturated and headroom power-admissibility modes."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


if len(sys.argv) != 3:
    raise SystemExit(
        "usage: test-power-gate-modes.py SUMMARIZER ADMISSIBLE_RUN_DIRECTORY"
    )

summarizer = Path(sys.argv[1]).resolve()
fixture = Path(sys.argv[2]).resolve()


def summarize(run_dir):
    output = run_dir / "summary-test.json"
    subprocess.run(
        [
            sys.executable,
            str(summarizer),
            str(run_dir / "gpu-telemetry.csv"),
            str(run_dir / "host-telemetry.csv"),
            str(run_dir / "requests.csv"),
            str(output),
            str(run_dir / "nvidia-before.txt"),
            str(run_dir / "nvidia-after.txt"),
            str(run_dir / "gpu1-vllm-metrics-before.txt"),
            str(run_dir / "gpu1-vllm-metrics-after.txt"),
        ],
        check=True,
    )
    return json.loads(output.read_text(encoding="utf-8"))


with tempfile.TemporaryDirectory(prefix="tower2-power-mode-test-") as temporary:
    run_dir = Path(temporary) / "run"
    shutil.copytree(fixture, run_dir)
    config_path = run_dir / "run-config.json"
    original_config = json.loads(config_path.read_text(encoding="utf-8"))

    saturated = summarize(run_dir)
    assert saturated["quality_gates"]["internal_admissible_candidate"] is True
    assert (
        saturated["quality_gates"]["per_gpu"]["0"]["loaded_power_mode"]
        == "saturated"
    )

    strict_headroom = dict(original_config)
    strict_headroom.update(
        {
            "gpu0_loaded_power_mode": "headroom",
            "max_warmup_power_gpu0_w": 310,
            "min_warmup_power_gpu0_w": 290,
            "gpu0_power_limit_w": 350,
            "headroom_max_sw_power_cap_fraction": 0,
        }
    )
    config_path.write_text(
        json.dumps(strict_headroom, indent=2) + "\n", encoding="utf-8"
    )
    strict = summarize(run_dir)
    strict_gpu0 = strict["quality_gates"]["per_gpu"]["0"]
    assert strict_gpu0["loaded_power_mode"] == "headroom"
    assert strict_gpu0["loaded_power_gate_pass"] is False
    assert strict_gpu0["sw_power_cap_active_fraction"] == 1
    assert strict["quality_gates"]["internal_admissible_candidate"] is False

    tolerant_headroom = dict(strict_headroom)
    tolerant_headroom["headroom_max_sw_power_cap_fraction"] = 1
    config_path.write_text(
        json.dumps(tolerant_headroom, indent=2) + "\n", encoding="utf-8"
    )
    tolerant = summarize(run_dir)
    assert (
        tolerant["quality_gates"]["per_gpu"]["0"]["loaded_power_gate_pass"]
        is True
    )
    assert tolerant["quality_gates"]["internal_admissible_candidate"] is True

    low_ceiling = dict(tolerant_headroom)
    low_ceiling["max_warmup_power_gpu0_w"] = 299
    config_path.write_text(
        json.dumps(low_ceiling, indent=2) + "\n", encoding="utf-8"
    )
    ceiling = summarize(run_dir)
    assert (
        ceiling["quality_gates"]["per_gpu"]["0"]["loaded_power_gate_pass"]
        is False
    )
    assert ceiling["quality_gates"]["internal_admissible_candidate"] is False

print("PASS: saturated fallback and headroom range/cap-fraction gates")
