#!/usr/bin/env python3
import importlib.util
import io
import json
import tarfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("audit_gemma4_extended.py")
SPEC = importlib.util.spec_from_file_location("audit_extended", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_expected_run_names_are_stable():
    assert MODULE.expected_run_name("dreamserver-1-pr-audit", 2) == "n1_gemma4-31b-q4_v2"
    assert MODULE.expected_run_name("wallstreet-investment-memo", 3) == \
        "gemma4-31b-q4_invest_memo_v3"
    assert MODULE.expected_run_name("wallstreet-board-presentation", 1) == \
        "gemma4-31b-q4_board_pres_v1"
    assert MODULE.expected_run_name("dreamserver-75-pr-audit", 3) == \
        "gemma4-31b-q4_75pr_v3"


def test_dependency_terminal_label_must_match_same_replicate(tmp_path, monkeypatch):
    logs = tmp_path / "logs" / "gemma4-31b-q4_board_pres_v2"
    logs.mkdir(parents=True)
    (logs / "label.json").write_text(json.dumps({
        "primary": "dependency-failure",
        "source_run": "gemma4-31b-q4_invest_memo_v1",
        "source_primary": "model-terminal-failure",
    }))
    record, errors, _ = MODULE.audit_extended_run(
        tmp_path,
        {
            "id": "wallstreet-board-presentation",
            "input_from": "wallstreet-investment-memo",
            "current_task_sha256": "unused",
        },
        rep=2,
        ordinal=5,
        lane_ports=[8000, 8001],
    )
    assert record["terminal_label"] == "dependency-failure"
    assert errors == [
        "dependency-failure source 'gemma4-31b-q4_invest_memo_v1' != "
        "'gemma4-31b-q4_invest_memo_v2'"
    ]


def test_subject_ref_audit_requires_every_pinned_ref(tmp_path):
    pin = tmp_path / "subject.json"
    pin.write_text("{}")
    run = tmp_path / "logs" / "n1_gemma4-31b-q4_v1"
    run.mkdir(parents=True)
    archive = run / "workspace_final.tar.gz"
    payload = b"base abcdef12 head 12345678\n"
    with tarfile.open(archive, "w:gz") as handle:
        info = tarfile.TarInfo("audit/trace.md")
        info.size = len(payload)
        handle.addfile(info, io.BytesIO(payload))
    suite = {
        "subject_pin": "subject.json",
        "subject_pin_sha256": MODULE.sha256(pin),
        "required_subject_shas": [
            "abcdef12aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "12345678bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "deadbeefcccccccccccccccccccccccccccccccc",
        ],
    }
    assert MODULE.audit_subject_refs(tmp_path, suite, run) == [
        "artifact does not identify pinned subject ref "
        "deadbeefcccccccccccccccccccccccccccccccc"
    ]
