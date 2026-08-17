#!/usr/bin/env python3
"""Unit tests for the deterministic delivery validator (synthetic cells)."""

import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import delivery_validator as dv  # noqa: E402

SPEC = {
    "p2_extract": [
        {"path": "extraction_results.json", "kind": "json"},
        {"path": "notes.md", "kind": "md"},
        {"path": "decisions", "kind": "dir"},
    ],
    "p1_testwrite": [
        {"path": "tests", "kind": "dir"},
        {"anyof": [{"path": "decisions", "kind": "dir"},
                   {"basename": "decisions.md", "kind": "md"}]},
    ],
}


def make_tar(path, files):
    """files: dict name -> bytes (name may contain dirs)."""
    with tarfile.open(path, "w:gz") as tf:
        for name, data in files.items():
            info = tarfile.TarInfo("./" + name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))


def make_cell(d, run_name, finish_reason="done_signal", tar_files=None,
              label=None, transcript_model_turns=3, with_summary=True,
              error_event=None):
    cell = Path(d) / run_name
    cell.mkdir(parents=True)
    if with_summary:
        (cell / "summary.json").write_text(json.dumps(
            {"finish_reason": finish_reason, "iterations": 10, "model": "m"}))
    if tar_files is not None:
        make_tar(cell / "workspace_final.tar.gz", tar_files)
    if label is not None:
        (cell / "label.json").write_text(json.dumps(label))
    lines = []
    for i in range(transcript_model_turns):
        lines.append(json.dumps({"type": "model", "iter": i + 1}))
        lines.append(json.dumps({"type": "tool", "name": "bash",
                                 "args": {"cmd": f"step{i}"}}))
    if error_event is not None:
        lines.append(json.dumps({"type": "error", **error_event}))
    (cell / "transcript.jsonl").write_text("\n".join(lines) + ("\n" if lines else ""))
    (cell / "receipt.json").write_text(json.dumps({"schema_version": 1}))
    return cell


# Verbatim llama-server HTTP 400 body from the real incident
# (p3_market_q38-diag-t03-nothink-s101_v1 attempt 1, 2026-08-17T13:33:21Z).
EXCEED_CTX_EVENT = {
    "error": "HTTP Error 400: Bad Request",
    "body": ('{"error":{"code":400,"message":"request (262339 tokens) exceeds '
             'the available context size (262144 tokens), try increasing it",'
             '"type":"exceed_context_size_error","n_prompt_tokens":262339,'
             '"n_ctx":262144}}'),
}


GOOD_P2 = {
    "extraction_results.json": b'{"records": []}',
    "notes.md": b"# notes\nreal content\n",
    "decisions/0001-choice.md": b"decision\n",
}


class TestDelivery(unittest.TestCase):
    def test_delivered_happy_path(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             tar_files=GOOD_P2)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertTrue(out["delivery"], out["reasons"])
            self.assertEqual(out["classification"], "delivered")
            self.assertEqual(out["family"], "p2_extract")

    def test_model_stopped_is_not_delivery(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             finish_reason="model_stopped", tar_files=GOOD_P2)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertFalse(out["delivery"])
            self.assertEqual(out["classification"], "completed-no-delivery")

    def test_missing_artifact_fails_delivery(self):
        with tempfile.TemporaryDirectory() as d:
            files = dict(GOOD_P2)
            del files["notes.md"]
            cell = make_cell(d, "p2_extract_q36-official-nothink-s211_v1",
                             tar_files=files)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertFalse(out["delivery"])
            self.assertTrue(any("notes.md" in r for r in out["reasons"]))

    def test_invalid_json_artifact_fails_schema(self):
        with tempfile.TemporaryDirectory() as d:
            files = dict(GOOD_P2)
            files["extraction_results.json"] = b"{not json"
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             tar_files=files)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertFalse(out["delivery"])

    def test_missing_tarball_fails(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             tar_files=None)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertFalse(out["delivery"])
            self.assertIn("workspace_final.tar.gz missing", out["reasons"])

    def test_api_error_is_infra(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             finish_reason="api_error: HTTP Error 502",
                             tar_files=GOOD_P2)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "infra")
            self.assertTrue(out["infra_rerun_eligible"])
            self.assertFalse(out["delivery"])

    def test_context_exhaustion_is_model_outcome_not_infra(self):
        # HTTP 400 exceed_context_size_error after real model turns is a
        # MODEL outcome (DEVIATIONS.md deviation 1): terminal, delivery
        # false, never quarantined, never rerun.
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-diag-t03-nothink-s101_v1",
                             finish_reason="api_error: HTTP Error 400: Bad Request",
                             tar_files=None, transcript_model_turns=5,
                             error_event=EXCEED_CTX_EVENT)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "context-exhausted")
            self.assertFalse(out["delivery"])
            self.assertFalse(out["infra_rerun_eligible"])
            self.assertTrue(any("context" in r for r in out["reasons"]))

    def test_context_exhaustion_token_pattern_alone_matches(self):
        # Same outcome when only the token-count message survives (no
        # exceed_context_size type string in the recorded body).
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-diag-t03-nothink-s101_v1",
                             finish_reason="api_error: HTTP Error 400: Bad Request",
                             tar_files=None, transcript_model_turns=2,
                             error_event={"error": "HTTP Error 400: Bad Request",
                                          "body": "request (262339 tokens) exceeds "
                                                  "the available context size "
                                                  "(262144 tokens), try increasing it"})
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "context-exhausted")
            self.assertFalse(out["infra_rerun_eligible"])

    def test_context_exhaustion_with_zero_model_turns_stays_infra(self):
        # A first-request overflow (no model turns) cannot be the model's own
        # prompt growth: config/infra problem, stays quarantine-eligible.
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-diag-t03-nothink-s101_v1",
                             finish_reason="api_error: HTTP Error 400: Bad Request",
                             tar_files=None, transcript_model_turns=0,
                             error_event=EXCEED_CTX_EVENT)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "infra")
            self.assertTrue(out["infra_rerun_eligible"])

    def test_non_context_api_errors_stay_infra(self):
        # Connection refused / 5xx / timeout api_errors with model turns and
        # a non-matching (or absent) error body remain infrastructure.
        cases = [
            ("api_error: <urlopen error [Errno 111] Connection refused>", None),
            ("api_error: HTTP Error 503: Service Unavailable",
             {"error": "HTTP Error 503: Service Unavailable", "body": "upstream down"}),
            ("api_error: The read operation timed out", None),
        ]
        for finish, ev in cases:
            with tempfile.TemporaryDirectory() as d:
                cell = make_cell(d, "p2_extract_q38-diag-t03-nothink-s101_v1",
                                 finish_reason=finish, tar_files=None,
                                 transcript_model_turns=3, error_event=ev)
                out = dv.validate_cell(cell, artifacts_spec=SPEC)
                self.assertEqual(out["classification"], "infra", finish)
                self.assertTrue(out["infra_rerun_eligible"], finish)

    def test_loop_label_classifies_loop_terminated(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             with_summary=False, tar_files=None,
                             label={"primary": "loop-run30",
                                    "metric": "consecutive_exact_run",
                                    "value": 30, "automated": True})
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "loop-terminated")
            self.assertFalse(out["delivery"])
            self.assertFalse(out["infra_rerun_eligible"])

    def test_timeout_label_classifies_timeout(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             with_summary=False, tar_files=None,
                             label={"primary": "timeout", "automated": True})
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "timeout")

    def test_dead_cell_no_summary_no_label_is_infra(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             with_summary=False, tar_files=None)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "infra")

    def test_zero_model_turns_is_infra(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p2_extract_q38-official-nothink-s101_v1",
                             tar_files=GOOD_P2, transcript_model_turns=0)
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertEqual(out["classification"], "infra")

    def test_anyof_basename(self):
        with tempfile.TemporaryDirectory() as d:
            cell = make_cell(d, "p1_testwrite_q38-official-nothink-s101_v1",
                             tar_files={"tests/test_x.py": b"def test(): pass\n",
                                        "notes/decisions.md": b"why\n"})
            out = dv.validate_cell(cell, artifacts_spec=SPEC)
            self.assertTrue(out["delivery"], out["reasons"])

    def test_family_parse_from_run_name(self):
        self.assertEqual(dv.family_from_run_name(
            "p2_extract_q38-official-nothink-s101_v1"), "p2_extract")
        self.assertEqual(dv.family_from_run_name(
            "p1_testwrite_q36-diag-t03-nothink-s307_v1"), "p1_testwrite")
        self.assertIsNone(dv.family_from_run_name("weird_name_v1"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
