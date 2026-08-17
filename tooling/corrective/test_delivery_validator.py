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
              label=None, transcript_model_turns=3, with_summary=True):
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
    (cell / "transcript.jsonl").write_text("\n".join(lines) + ("\n" if lines else ""))
    (cell / "receipt.json").write_text(json.dumps({"schema_version": 1}))
    return cell


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
