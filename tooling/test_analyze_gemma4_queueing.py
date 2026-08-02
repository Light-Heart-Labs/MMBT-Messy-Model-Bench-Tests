#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).with_name("analyze_gemma4_queueing.py")
SPEC = importlib.util.spec_from_file_location("queueing", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def request(wall, prompt_ms=1000, predicted_ms=4000):
    return {
        "wall_seconds": wall,
        "timings": {"prompt_ms": prompt_ms, "predicted_ms": predicted_ms},
        "tokens_evaluated": 100,
        "tokens_predicted": 200,
    }


def test_queueing_analyzer_separates_service_waves_and_labels_estimate(tmp_path):
    source = tmp_path / "summary.json"
    source.write_text(json.dumps({
        "concurrency_results": [{
            "concurrency": 8,
            "aggregate_decode_tokens_per_second_wall": 100.0,
            "requests": [
                request(7.0), request(7.2), request(7.1), request(7.3),
                request(14.0), request(14.2), request(14.1), request(14.3),
            ],
        }],
    }))
    result = MODULE.analyze(source, slots=4, concurrency=8)
    assert result["first_wave"]["median_wall_s"] == 7.15
    assert result["queued_second_wave"]["median_wall_s"] == 14.15
    assert result["derived"]["second_wave_wall_penalty_s"] == 7.0
    assert result["derived"]["estimated_queue_wait_delta_s"] == 7.0
    assert "estimate, not a direct server-side queue timestamp" in result["methodology"]


def test_queueing_analyzer_rejects_incomplete_request_inventory(tmp_path):
    source = tmp_path / "summary.json"
    source.write_text(json.dumps({
        "concurrency_results": [{"concurrency": 8, "requests": [request(7.0)]}],
    }))
    try:
        MODULE.analyze(source, slots=4, concurrency=8)
    except ValueError as exc:
        assert "expected 8 request results" in str(exc)
    else:
        raise AssertionError("incomplete concurrency evidence was accepted")
