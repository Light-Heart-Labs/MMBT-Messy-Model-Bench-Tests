#!/usr/bin/env python3
"""Regression test: canonical retries never append to previous evidence."""

import importlib.util
import tempfile
from pathlib import Path


HARNESS_PATH = Path(__file__).resolve().parents[1] / "harness.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("mmbt_harness", HARNESS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    harness = load_harness()
    with tempfile.TemporaryDirectory(prefix="mmbt-log-isolation-") as tmp:
        logs = Path(tmp) / "logs"
        run_name = "p1_bugfix_test_v1"
        run_dir = logs / run_name
        run_dir.mkdir(parents=True)
        (run_dir / "receipt.json").write_text("{}\n", encoding="utf-8")
        (run_dir / "transcript.jsonl").write_text(
            '{"type":"model"}\n', encoding="utf-8"
        )

        archived = harness.prepare_log_dir(run_dir, run_name)
        assert archived is not None
        assert run_dir.is_dir()
        assert not list(run_dir.iterdir())
        assert (archived / "receipt.json").is_file()
        assert (archived / "transcript.jsonl").is_file()
        assert archived.parent == logs / "_invalid"

        (run_dir / "summary.json").write_text("{}\n", encoding="utf-8")
        (run_dir / "workspace_final.tar.gz").write_bytes(b"complete")
        try:
            harness.prepare_log_dir(run_dir, run_name)
        except RuntimeError as exc:
            assert "completed benchmark evidence" in str(exc)
        else:
            raise AssertionError("completed evidence was not protected")

        assert (run_dir / "summary.json").is_file()
        assert (run_dir / "workspace_final.tar.gz").is_file()
        print(f"archived={archived}")
        print("completed-evidence-guard=PASS")


if __name__ == "__main__":
    main()
