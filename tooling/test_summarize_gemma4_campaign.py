#!/usr/bin/env python3
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("summarize_gemma4_campaign.py")
SPEC = importlib.util.spec_from_file_location("summary", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def record(name, task, verdict, finish, wall, tokens, tps, telemetry=None):
    return {
        "run_name": name,
        "task": task,
        "verdict": verdict,
        "summary": {"finish_reason": finish, "elapsed_s": wall, "total_completion_tokens": tokens},
        "cost": {"throughput": {"completion_tps_avg": tps}},
        "telemetry": telemetry,
    }


def test_aggregate_keeps_finish_and_quality_axes_separate():
    rows = [
        record("a", "p1_bugfix", "PASS", "done_signal", 10, 100, 20,
               {"coverage": 0.9, "mean_power_w": 400, "mean_sm_util_pct": 90, "max_temp_c": 70}),
        record("b", "p1_bugfix", "FAIL", "done_signal", 20, 200, 30),
        record("c", "p2_extract", "STRUCTURAL_PASS", "model_stopped", 30, 300, 40),
    ]
    result = MODULE.aggregate_records(rows)
    assert result["raw_passes"] == 2
    assert result["finish_reasons"] == {"done_signal": 2, "model_stopped": 1}
    assert result["model_call_completion_tps"]["median"] == 30
    assert result["per_task"]["p1_bugfix"]["raw_passes"] == 1
    assert result["telemetry"]["runs"] == 1


def test_markdown_explicitly_rejects_done_equals_pass():
    document = {"target_n": 1, "aggregate": MODULE.aggregate_records([])}
    rendered = MODULE.markdown(document)
    assert "A `done_signal` is a finish behavior, not a pass" in rendered
    assert "Raw grader verdicts only" in rendered


def test_terminal_label_is_scored_as_distinct_nonpass_without_fake_grade():
    terminal = {
        "run_name": "p3_market_gemma4-31b-q4_v1",
        "task": "p3_market",
        "verdict": None,
        "summary": None,
        "terminal_label": "identical-call-loop",
        "cost": {
            "wall_s": 45,
            "tokens": {"completion_total": 1234},
            "throughput": {"completion_tps_avg": 27.4},
        },
        "telemetry": {
            "coverage": 0.92, "mean_power_w": 450,
            "mean_sm_util_pct": 95, "max_temp_c": 76,
        },
    }
    result = MODULE.aggregate_records([terminal])
    assert result["completed"] == 1
    assert result["normal_completed"] == 0
    assert result["terminal_outcomes"] == 1
    assert result["graded"] == 0
    assert result["scored_outcomes"] == 1
    assert result["raw_passes"] == 0
    assert result["raw_pass_rate"] == 0.0
    assert result["finish_reasons"] == {"terminal:identical-call-loop": 1}
    assert result["quality_outcomes"] == {"TERMINAL:identical-call-loop": 1}
    assert result["wall_s"]["sum"] == 45
    assert result["completion_tokens"]["sum"] == 1234
