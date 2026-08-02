#!/usr/bin/env python3
import importlib.util
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).with_name("validate_gemma4_comparison_sources.py")
SPEC = importlib.util.spec_from_file_location("comparison_sources", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_expected_comparator_set_is_explicit_and_complete():
    assert MODULE.EXPECTED_IDS == {
        "qwen3.6-27b-awq",
        "qwen3-coder-next-awq",
        "qwen3.6-35b-a3b-awq",
        "qwen3.5-397b-a17b-q3-nothink",
        "deepseek-v4-flash-0731",
    }


def test_manifest_keeps_raw_corrected_and_missing_cohort_distinct():
    manifest = json.loads(
        Path(__file__).with_name("gemma4-comparison-sources.json").read_text()
    )
    rows = {row["id"]: row for row in manifest["comparators"]}
    assert rows["deepseek-v4-flash-0731"]["canonical"] == {
        "cohort": "12 families x N=3",
        "raw_passes": 23,
        "corrected_passes": 35,
        "total": 36,
    }
    assert rows["qwen3.5-397b-a17b-q3-nothink"]["canonical"]["total"] == 120
    assert rows["qwen3.6-35b-a3b-awq"]["canonical"] is None
    assert any("not a global SOTA claim" in rule for rule in manifest["comparison_rules"])


def test_mutable_scorecard_is_verified_at_the_pinned_source_commit():
    manifest = json.loads(
        Path(__file__).with_name("gemma4-comparison-sources.json").read_text()
    )
    assert manifest["source_repository_commit"] == (
        "dc8f57d443aeccba652a33852fda32d37cd701f3"
    )
    scorecard = next(
        row for row in manifest["source_documents"] if row["path"] == "SCORECARD.md"
    )
    assert scorecard["verify_at_source_commit"] is True


def test_git_blob_hash_uses_exact_git_show_bytes(monkeypatch, tmp_path):
    payload = b"pre-campaign scorecard\n"

    def fake_run(command, capture_output, check):
        assert command[-1] == "abc123:SCORECARD.md"
        assert capture_output is True
        assert check is False
        return SimpleNamespace(returncode=0, stdout=payload)

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)
    assert MODULE.git_blob_sha256(tmp_path, "abc123", "SCORECARD.md") == hashlib.sha256(
        payload
    ).hexdigest()
