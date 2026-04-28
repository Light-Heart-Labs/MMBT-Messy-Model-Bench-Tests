#!/usr/bin/env python3
"""CI-failure grader: re-runs the CI checks (ruff + pytest) against the agent's
delivered repo. Pass = both checks green.

Also captures secondary signals: how many fixes were needed (commit count),
whether the changelog was updated, whether `# noqa` / disabled tests were
introduced (which would be a soft fail per the task rules).

Usage:
    phase2_ci_failure_grade.py <workspace_dir> [--out grade.json]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None, timeout=300):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def grade(workspace: Path) -> dict:
    if not (workspace / "pyproject.toml").exists():
        return {"task": "ci_failure", "verdict": "MISSING_OUTPUT",
                "notes": "no pyproject.toml in workspace"}

    # Install package (in case it's not already). --break-system-packages
    # because some host Pythons enforce PEP 668; we're in a throwaway grading
    # env where contaminating user-site is fine.
    install = run(["pip", "install", "-q", "--break-system-packages", "-e", ".[dev]"],
                  cwd=workspace, timeout=120)
    install_ok = install["rc"] == 0

    # Run ruff
    ruff_r = run(["ruff", "check", "src/", "tests/"], cwd=workspace, timeout=60)
    ruff_clean = ruff_r["rc"] == 0
    ruff_issues = 0
    m = re.search(r"Found (\d+) error", ruff_r["stdout"])
    if m:
        ruff_issues = int(m.group(1))
    elif "All checks passed" in ruff_r["stdout"] or ruff_r["rc"] == 0:
        ruff_issues = 0

    # Run pytest
    pyt_r = run(["pytest", "-q", "--tb=no"], cwd=workspace, timeout=180)
    pyt_clean = pyt_r["rc"] == 0
    pyt_passed = pyt_failed = 0
    m_p = re.search(r"(\d+) passed", pyt_r["stdout"])
    m_f = re.search(r"(\d+) failed", pyt_r["stdout"])
    if m_p:
        pyt_passed = int(m_p.group(1))
    if m_f:
        pyt_failed = int(m_f.group(1))

    # Soft-fail signals: did the agent take shortcuts?
    src_dir = workspace / "src"
    tests_dir = workspace / "tests"
    noqa_count = 0
    skip_count = 0
    for d in [src_dir, tests_dir]:
        if not d.is_dir():
            continue
        for f in d.rglob("*.py"):
            try:
                content = f.read_text()
                noqa_count += len(re.findall(r"#\s*noqa", content))
                skip_count += len(re.findall(r"@pytest\.mark\.skip|@pytest\.mark\.xfail", content))
            except Exception:
                pass
    # Also check pyproject.toml didn't add lint ignores
    pyproject = (workspace / "pyproject.toml").read_text() if (workspace / "pyproject.toml").exists() else ""
    suspicious_pyproject = any(
        s in pyproject for s in ['ignore = ["F401', 'ignore = ["E501', '"--tb=no" -p no:cacheprovider']
    )

    # Verdict
    verdict = "PASS" if (ruff_clean and pyt_clean and noqa_count == 0 and skip_count == 0) else "FAIL"

    # Commit count (how many fixes the agent broke things into)
    git_log = run(["git", "log", "--oneline"], cwd=workspace, timeout=10)
    commits = len(git_log["stdout"].strip().splitlines()) if git_log["rc"] == 0 else 0

    # Changelog mention
    changelog = workspace / "CHANGELOG.md"
    changelog_extended = False
    if changelog.exists():
        text = changelog.read_text()
        if "v0.3.2" in text or "0.3.2" in text or "fix" in text.lower():
            changelog_extended = True

    diagnosis = workspace / "diagnosis.md"
    diagnosis_present = diagnosis.exists()

    return {
        "task": "ci_failure",
        "verdict": verdict,
        "ruff": {
            "exit_code": ruff_r["rc"],
            "issue_count": ruff_issues,
            "clean": ruff_clean,
        },
        "pytest": {
            "exit_code": pyt_r["rc"],
            "passed": pyt_passed,
            "failed": pyt_failed,
            "clean": pyt_clean,
        },
        "shortcut_signals": {
            "noqa_count": noqa_count,
            "skipped_or_xfail_test_count": skip_count,
            "suspicious_pyproject_changes": suspicious_pyproject,
        },
        "process_signals": {
            "commit_count": commits,
            "changelog_extended": changelog_extended,
            "diagnosis_present": diagnosis_present,
            "install_ok": install_ok,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    result = grade(Path(args.workspace).resolve())
    out_path = Path(args.out) if args.out else (Path(args.workspace) / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
