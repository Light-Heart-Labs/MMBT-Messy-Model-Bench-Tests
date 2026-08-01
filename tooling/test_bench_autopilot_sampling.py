#!/usr/bin/env python3
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("bench_autopilot.py")
SPEC = importlib.util.spec_from_file_location("bench_autopilot", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_model_card_sampling_reaches_child_environment():
    env = MODULE.benchmark_environment(
        {
            "benchmark_temperature": 1.0,
            "benchmark_top_p": 0.95,
            "benchmark_top_k": 64,
        },
        {"PRESERVED": "yes", "BENCH_TOP_K": "stale"},
    )
    assert env["PRESERVED"] == "yes"
    assert env["BENCH_TEMP"] == "1.0"
    assert env["BENCH_TOP_P"] == "0.95"
    assert env["BENCH_TOP_K"] == "64"


def test_unset_sampling_does_not_leak_parent_overrides():
    env = MODULE.benchmark_environment(
        {},
        {
            "PRESERVED": "yes",
            "BENCH_TEMP": "9",
            "BENCH_TOP_P": "0.1",
            "BENCH_TOP_K": "1",
        },
    )
    assert env == {"PRESERVED": "yes"}
