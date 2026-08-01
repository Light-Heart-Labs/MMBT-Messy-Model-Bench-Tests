#!/usr/bin/env python3
"""Regression checks for cache-safe and sandboxed MMBT grading."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path


TOOLING = Path(__file__).resolve().parents[1]
GRADERS = TOOLING / "graders"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_source_tree_comparison() -> None:
    phase1 = load("phase1_grade", GRADERS / "phase1_grade.py")
    with tempfile.TemporaryDirectory(prefix="mmbt-grade-tree-") as tmp:
        root = Path(tmp)
        before = root / "before"
        after = root / "after"
        before.mkdir()
        after.mkdir()
        (before / "source.py").write_text("same\n", encoding="utf-8")
        (after / "source.py").write_text("same\n", encoding="utf-8")
        (after / "__pycache__").mkdir()
        (after / "__pycache__" / "source.pyc").write_bytes(b"runtime cache")
        (after / ".coverage").write_text("runtime cache", encoding="utf-8")
        assert phase1.source_tree_changes(before, after) == []

        (after / "source.py").write_text("changed\n", encoding="utf-8")
        assert phase1.source_tree_changes(before, after) == ["modified:source.py"]


def test_ci_grader_commands_and_counts() -> None:
    ci = load("phase2_ci_failure_grade", GRADERS / "phase2_ci_failure_grade.py")
    calls: list[list[str]] = []

    def fake_run(cmd, cwd=None, timeout=300):
        calls.append([str(part) for part in cmd])
        if "ruff" in cmd:
            return {"rc": 0, "stdout": "All checks passed!\n", "stderr": ""}
        if "pytest" in cmd:
            return {"rc": 0, "stdout": "....... [100%]\n7 passed in 0.01s\n", "stderr": ""}
        if cmd and cmd[0] == "git":
            return {"rc": 0, "stdout": "a fix\nb fix\nc fix\n", "stderr": ""}
        return {"rc": 0, "stdout": "", "stderr": ""}

    ci.run = fake_run
    with tempfile.TemporaryDirectory(prefix="mmbt-grade-ci-") as tmp:
        workspace = Path(tmp)
        (workspace / "src").mkdir()
        (workspace / "tests").mkdir()
        (workspace / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
        (workspace / "CHANGELOG.md").write_text("v0.3.2 fix\n", encoding="utf-8")
        (workspace / "diagnosis.md").write_text("diagnosis\n", encoding="utf-8")
        result = ci.grade(workspace)

    assert result["verdict"] == "PASS"
    assert result["pytest"]["passed"] == 7
    assert result["process_signals"]["commit_count"] == 3
    assert calls[0][:3] == [sys.executable, "-m", "pip"]
    assert any(call[:3] == [sys.executable, "-m", "ruff"] for call in calls)
    pytest_call = next(call for call in calls if call[:3] == [sys.executable, "-m", "pytest"])
    assert "-q" not in pytest_call
    assert any(call[:3] == ["git", "-c", f"safe.directory={workspace}"] for call in calls)


def test_ci_wrapper_is_sandboxed() -> None:
    wrapper = (TOOLING / "scripts" / "grade_microbench.sh").read_text(encoding="utf-8")
    ci_case = wrapper.split("p2_ci)", 1)[1].split(";;", 1)[0]
    assert "docker run --rm" in ci_case
    assert "bench-sandbox:latest" in ci_case
    assert "/g/phase2_ci_failure_grade.py" in ci_case


def test_writing_grader_accepts_spec_equivalent_language() -> None:
    writing = load(
        "phase3_writing_editing_grade",
        GRADERS / "phase3_writing_editing_grade.py",
    )
    with tempfile.TemporaryDirectory(prefix="mmbt-grade-writing-") as tmp:
        workspace = Path(tmp)
        (workspace / "customer_email.md").write_text(
            "Friday's service disruption affected customers. We will honor the "
            "SLA credit; contact support to request it.\n",
            encoding="utf-8",
        )
        customer = writing.grade_audience(
            workspace,
            "customer_email",
            {"filename": "customer_email.md", "max_words": 350},
        )
        assert customer["verdict"] == "PASS"
        assert customer["required_content_hits"][0]["matched"] == "service disruption"

        (workspace / "legal_summary.md").write_text(
            "The incident ran from 14:11 UTC to 18:24 UTC. The 99.9% monthly "
            "uptime SLA was breached. Four accounts had downstream harm. "
            "Requests citing lost trust are relationship-driven and should be "
            "handled case-by-case.\n",
            encoding="utf-8",
        )
        legal = writing.grade_audience(
            workspace,
            "legal_summary",
            {"filename": "legal_summary.md", "max_words": 400},
        )
        assert legal["verdict"] == "PASS"
        assert legal["prohibited_content_hits"] == []

        (workspace / "legal_summary.md").write_text(
            (workspace / "legal_summary.md").read_text(encoding="utf-8")
            + "We are committed to delighting every customer.\n",
            encoding="utf-8",
        )
        legal_marketing = writing.grade_audience(
            workspace,
            "legal_summary",
            {"filename": "legal_summary.md", "max_words": 400},
        )
        assert legal_marketing["verdict"] == "FAIL"
        assert legal_marketing["prohibited_content_hits"] == ["we are committed"]


def main() -> None:
    test_source_tree_comparison()
    test_ci_grader_commands_and_counts()
    test_ci_wrapper_is_sandboxed()
    test_writing_grader_accepts_spec_equivalent_language()
    print("grader-isolation-regressions=PASS")


if __name__ == "__main__":
    main()
