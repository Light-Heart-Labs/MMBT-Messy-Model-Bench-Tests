#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).with_name("audit_gemma4_campaign.py")
SPEC = importlib.util.spec_from_file_location("audit", SCRIPT)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUDIT)


def write_json(path, value):
    path.write_text(json.dumps(value))


def make_run(tmp_path, telemetry=True):
    run = tmp_path / "p2_extract_gemma4-31b-q4_v1"
    run.mkdir()
    write_json(run / "receipt.json", {
        "harness": {"git_dirty": False, "git_sha": "abc"},
        "vllm": {"served_model_name": AUDIT.MODEL, "api_url": "http://127.0.0.1:8000/v1/chat/completions"},
        "inference_request_defaults": {
            "temperature": 1.0, "top_p": 0.95, "top_k": 64,
            "max_model_len": 262144, "max_output_tokens_cap": 262144,
        },
        "serving": {
            "manifest": {"payload": {"artifact": {"sha256": AUDIT.MODEL_SHA}}},
            "host_processes": [{"exe_sha256": AUDIT.SERVER_SHA}],
            "endpoint_models": {"payload": {"data": [{"id": AUDIT.MODEL}]}},
        },
        "hardware": {"nvidia_smi": ["0, GPU, driver, 500.00 W", "1, GPU, driver, 500.00 W"]},
    })
    write_json(run / "summary.json", {
        "model": AUDIT.MODEL, "finish_reason": "done_signal", "elapsed_s": 10,
        "iterations": 1, "total_completion_tokens": 20, "total_prompt_tokens": 30,
    })
    (run / "transcript.jsonl").write_text(json.dumps({
        "type": "model", "finish_reason": "stop", "completion_tokens": 20,
    }) + "\n")
    (run / "workspace_final.tar.gz").write_bytes(b"archive")
    write_json(run / "cost.json", {
        "run_name": run.name, "model": AUDIT.MODEL, "wall_s": 10,
        "iters": 1, "tokens": {"completion_total": 20, "prompt_total": 30},
    })
    if telemetry:
        write_json(run / "gpu_telemetry.json", {
            "attribution": {"active_gpu_ids_observed": ["0"]},
            "sampling": {"coverage_fraction_of_wall": 0.95},
            "active_gpu": {"configured_cap_w": 500.0, "mean_power_w": 400,
                           "mean_sm_util_pct": 90, "max_temp_c": 70},
            "cpu_package_shared_context": {"mean_power_w": 100},
        })
    return run


def test_complete_run_passes_strict_evidence_audit(tmp_path):
    record, errors, warnings = AUDIT.audit_run(make_run(tmp_path), False, False)
    assert errors == []
    assert warnings == []
    assert record["telemetry"]["gpu"] == ["0"]


def test_deployed_default_root_is_repository_parent_of_tooling():
    deployed = Path("/home/michael/bench-gemma4-31b-q4/tooling/audit_gemma4_campaign.py")
    assert AUDIT.default_root(deployed) == Path("/home/michael/bench-gemma4-31b-q4")


def test_pretelemetry_exception_is_explicit_and_warned(tmp_path):
    record, errors, warnings = AUDIT.audit_run(make_run(tmp_path, telemetry=False), True, False)
    assert errors == []
    assert warnings == ["pre-telemetry valid attempt; supplemental telemetry required"]
    assert record["telemetry"] is None


def test_wrong_sampling_fails(tmp_path):
    run = make_run(tmp_path)
    receipt = json.loads((run / "receipt.json").read_text())
    receipt["inference_request_defaults"]["temperature"] = 0.3
    write_json(run / "receipt.json", receipt)
    _, errors, _ = AUDIT.audit_run(run, False, False)
    assert "wrong temperature: 0.3" in errors


def test_supplement_mapping_parser_is_fail_closed():
    mappings, errors = AUDIT.parse_supplement_mappings([
        "canonical_v1=supplement_v1",
        "canonical_v1=duplicate",
        "malformed",
    ])
    assert mappings == {"canonical_v1": "supplement_v1"}
    assert errors == [
        "duplicate pretelemetry supplement mapping for canonical_v1",
        "invalid pretelemetry supplement mapping 'malformed'; expected "
        "CANONICAL_RUN=SUPPLEMENTAL_RUN",
    ]


def test_terminal_outcome_requires_preserved_receipt_and_transcript(tmp_path):
    run = tmp_path / "p3_market_gemma4-31b-q4_v1"
    run.mkdir()
    write_json(run / "label.json", {"primary": "identical-call-loop"})
    _, errors, _ = AUDIT.audit_run(run, False, False)
    assert errors == [
        "terminal outcome missing preserved receipt.json",
        "terminal outcome missing preserved transcript.jsonl",
        "terminal outcome missing preserved cost.json",
        "terminal outcome missing preserved gpu_telemetry.json",
    ]


def test_terminal_outcome_passes_only_with_full_identity_cost_and_telemetry(tmp_path):
    run = make_run(tmp_path)
    (run / "summary.json").unlink()
    (run / "workspace_final.tar.gz").unlink()
    write_json(run / "label.json", {
        "primary": "identical-call-loop",
        "labeled_at": "2026-08-02T00:00:10+00:00",
    })
    telemetry = json.loads((run / "gpu_telemetry.json").read_text())
    telemetry["sampling"]["window_source"] = (
        "receipt.json:captured_at..label.json:labeled_at"
    )
    write_json(run / "gpu_telemetry.json", telemetry)
    record, errors, warnings = AUDIT.audit_run(run, False, True)
    assert errors == []
    assert warnings == []
    assert record["outcome_kind"] == "terminal-label"
    assert record["finish_reason"] == "terminal:identical-call-loop"
    assert record["grade_verdict"] is None


def test_dependency_failure_requires_source_evidence(tmp_path):
    run = tmp_path / "gemma4-31b-q4_board_pres_v1"
    run.mkdir()
    write_json(run / "label.json", {"primary": "dependency-failure"})
    _, errors, _ = AUDIT.audit_run(run, False, False)
    assert errors == ["dependency-failure label lacks source evidence"]


def test_invalid_attempt_requires_hash_tied_classification_and_completed_replacement(tmp_path):
    invalid_root = tmp_path / "logs" / "_invalid"
    attempt = invalid_root / "p1_refactor_gemma4-31b-q4_v3-timeout"
    attempt.mkdir(parents=True)
    (attempt / "receipt.json").write_bytes(b"receipt")
    incident = tmp_path / "incident.json"
    write_json(incident, {"classification": "test"})
    classifications = tmp_path / "classifications.json"
    write_json(classifications, {
        "attempts": {
            attempt.name: {
                "source_run": "p1_refactor_gemma4-31b-q4_v3",
                "classification": "infrastructure-invalid",
                "reason_code": "server-timeout",
                "incident_document": incident.name,
                "classified_before_grade": True,
                "affirmative_evidence": ["exact timeout"],
                "expected_files": {
                    "receipt.json": AUDIT.sha256(attempt / "receipt.json"),
                },
                "replacement": {
                    "required": True,
                    "canonical_run": "p1_refactor_gemma4-31b-q4_v3",
                    "status": "completed",
                },
            },
        },
    })
    records, source, errors = AUDIT.audit_invalid_attempts(
        invalid_root, classifications, "gemma4-31b-q4",
    )
    assert errors == []
    assert records[0]["files"]["receipt.json"]["sha256"] == AUDIT.sha256(
        attempt / "receipt.json"
    )
    assert source["sha256"] == AUDIT.sha256(classifications)

    document = json.loads(classifications.read_text())
    document["attempts"][attempt.name]["replacement"]["status"] = "pending"
    write_json(classifications, document)
    _, _, errors = AUDIT.audit_invalid_attempts(
        invalid_root, classifications, "gemma4-31b-q4",
    )
    assert errors == [f"{attempt.name}: exact canonical replacement is not completed"]


def test_timeout_replacement_requires_corrected_server_control(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    run = make_run(logs)
    receipt = json.loads((run / "receipt.json").read_text())
    receipt["serving"]["host_processes"][0]["argv"] = [
        "llama-server", "--timeout", "14400",
    ]
    write_json(run / "receipt.json", receipt)
    record = {
        "attempt": "p2_extract_gemma4-31b-q4_v1-timeout",
        "classification": {
            "reason_code": "server-transport-timeout-below-native-envelope",
            "replacement": {"canonical_run": run.name},
        },
    }
    assert AUDIT.audit_replacement_controls(logs, [record]) == []
    receipt["serving"]["host_processes"][0]["argv"][-1] = "3600"
    write_json(run / "receipt.json", receipt)
    assert AUDIT.audit_replacement_controls(logs, [record]) == [
        f"{record['attempt']}: replacement does not prove a >=14400-second server timeout"
    ]
