#!/usr/bin/env python3
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).with_name("capture_gemma4_grader_manifest.py")
SPEC = importlib.util.spec_from_file_location("grader_manifest", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_fingerprint_files_hashes_and_fails_closed(tmp_path):
    present = tmp_path / "present.py"
    present.write_bytes(b"print('fixed grader')\n")
    files, errors = MODULE.fingerprint_files(tmp_path, ["present.py", "missing.json"])
    assert files["present.py"]["bytes"] == len(present.read_bytes())
    assert files["present.py"]["sha256"] == MODULE.sha256(present)
    assert errors == ["missing grader input: missing.json"]


def test_manifest_covers_all_canonical_task_graders():
    joined = "\n".join(MODULE.GRADER_FILES)
    for task in MODULE.TASKS:
        family = task.split("_", 1)[0]
        assert family in {"p1", "p2", "p3"}
    assert "phase1_grade.py" in joined
    assert "phase2_hallucination_grade.py" in joined
    assert "phase3_project_mgmt_grade.py" in joined
