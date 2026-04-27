#!/usr/bin/env python3
"""Code-task grader: runs against a delivered repo (the agent's /workspace) and
captures programmatic deltas vs the starter baseline.

Reads the agent's repo from --workspace, the starter from --baseline, and writes
a JSON result to --out. Run inside the sandbox image so pytest/ruff/etc are
available.

What it captures:
- pytest pass rate (test_passed / test_total) — both before and after
- pytest-cov line coverage % — both before and after
- ruff check issue count — both before and after
- benchmarks/bench.py wall time on a fixed-size synthetic log — both before and after
- file-level diffs: deleted modules, new modules, line-count delta
- git: commit count, commit-message stats (avg length, first-line %)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def run(cmd, cwd, timeout=600, env=None):
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, env=full_env)
        return {"rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
    except subprocess.TimeoutExpired:
        return {"rc": -1, "stdout": "", "stderr": f"timeout after {timeout}s"}


def measure_pytest(repo_path, marker=""):
    """Run pytest and parse the summary line for passed/failed/error counts."""
    r = run(["python3", "-m", "pytest", "--tb=no", "-q", "--no-header"],
            cwd=repo_path, timeout=600)
    out = r["stdout"] + "\n" + r["stderr"]
    # Try to find the summary line "X passed, Y failed in Z.zs"
    passed = failed = errors = skipped = 0
    for m in re.finditer(r"(\d+)\s+(passed|failed|errors?|skipped)", out):
        n, kind = int(m.group(1)), m.group(2)
        if kind == "passed": passed = n
        elif kind == "failed": failed = n
        elif kind.startswith("error"): errors = n
        elif kind == "skipped": skipped = n
    total = passed + failed + errors  # don't count skipped as failure
    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "total": total,
        "pass_rate": (passed / total) if total > 0 else None,
        "rc": r["rc"],
        "tail": out[-1500:],
    }


def measure_coverage(repo_path):
    """Run pytest with coverage and parse the line-coverage percentage."""
    r = run(["python3", "-m", "pytest", "--cov=logalyzer", "--cov-report=term", "-q",
             "--no-header", "--tb=no"], cwd=repo_path, timeout=600)
    out = r["stdout"] + "\n" + r["stderr"]
    # coverage prints a TOTAL line like:  TOTAL    234   45    81%
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", out)
    pct = int(m.group(1)) if m else None
    return {"line_coverage_pct": pct, "rc": r["rc"], "tail": out[-1500:]}


def measure_ruff(repo_path):
    """Run ruff and count issues."""
    r = run(["python3", "-m", "ruff", "check", "--no-fix", "--output-format=concise", "logalyzer", "tests"],
            cwd=repo_path, timeout=120)
    out = r["stdout"] + "\n" + r["stderr"]
    # Each issue is a line. Count non-empty lines that aren't summary.
    lines = [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("Found")]
    # Filter out anything that's clearly a summary
    issue_lines = [ln for ln in lines if ":" in ln]
    return {"issue_count": len(issue_lines), "rc": r["rc"], "tail": out[-2000:]}


def measure_benchmark(repo_path, size_mb=10):
    """Run benchmarks/bench.py if present and parse the elapsed seconds."""
    bench = Path(repo_path) / "benchmarks" / "bench.py"
    if not bench.exists():
        return {"elapsed_s": None, "skipped": "no benchmarks/bench.py"}
    r = run(["python3", "benchmarks/bench.py", "--size", str(size_mb)],
            cwd=repo_path, timeout=600)
    out = r["stdout"] + "\n" + r["stderr"]
    m = re.search(r"elapsed:\s*([\d.]+)\s*s", out)
    elapsed = float(m.group(1)) if m else None
    return {"elapsed_s": elapsed, "rc": r["rc"], "tail": out[-1500:]}


def measure_git(repo_path):
    """Capture commit count, message stats."""
    rp = str(repo_path)
    log_r = run(["git", "-C", rp, "log", "--all", "--format=%H%x09%s%x09%b%x1e"],
                cwd=rp, timeout=30, env={"GIT_CONFIG_GLOBAL": "/dev/null"})
    if log_r["rc"] != 0:
        return {"commit_count": 0, "error": log_r["stderr"][:500]}
    raw = log_r["stdout"].strip("\x1e\n")
    if not raw:
        return {"commit_count": 0}
    commits = []
    for entry in raw.split("\x1e"):
        parts = entry.strip("\n").split("\t", 2)
        if len(parts) >= 2:
            commits.append({"sha": parts[0][:10], "subject": parts[1],
                            "body_len": len(parts[2]) if len(parts) > 2 else 0})
    msg_lengths = [len(c["subject"]) for c in commits]
    return {
        "commit_count": len(commits),
        "avg_subject_len": sum(msg_lengths) / len(msg_lengths) if msg_lengths else 0,
        "tags": run(["git", "-C", rp, "tag"], cwd=rp).get("stdout", "").split(),
    }


def measure_files(repo_path):
    """Capture file-level facts about the repo."""
    rp = Path(repo_path)
    py_files = list(rp.rglob("*.py"))
    # Filter out venv etc
    py_files = [p for p in py_files if ".git" not in p.parts and "venv" not in p.parts]
    total_loc = 0
    for p in py_files:
        try:
            total_loc += sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
        except Exception:
            pass
    return {
        "py_file_count": len(py_files),
        "total_python_loc": total_loc,
        "experimental_py_present": (rp / "logalyzer" / "experimental.py").exists(),
    }


def measure_repo(repo_path, label):
    """Run all measurements against a repo and return a dict."""
    print(f"=== {label}: {repo_path} ===", file=sys.stderr)
    print("  pytest…", file=sys.stderr)
    pytest_result = measure_pytest(repo_path)
    print("  coverage…", file=sys.stderr)
    cov_result = measure_coverage(repo_path)
    print("  ruff…", file=sys.stderr)
    ruff_result = measure_ruff(repo_path)
    print("  bench…", file=sys.stderr)
    bench_result = measure_benchmark(repo_path)
    print("  git…", file=sys.stderr)
    git_result = measure_git(repo_path)
    print("  files…", file=sys.stderr)
    files_result = measure_files(repo_path)
    return {
        "label": label,
        "path": str(repo_path),
        "pytest": pytest_result,
        "coverage": cov_result,
        "ruff": ruff_result,
        "benchmark": bench_result,
        "git": git_result,
        "files": files_result,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True, help="Path to the agent's delivered repo")
    ap.add_argument("--baseline", required=True, help="Path to the starter baseline repo")
    ap.add_argument("--out", required=True, help="Output JSON file path")
    args = ap.parse_args()

    # Copy baseline somewhere writable so pytest/coverage/etc can write artifacts
    with tempfile.TemporaryDirectory() as td:
        baseline_copy = Path(td) / "baseline"
        shutil.copytree(args.baseline, baseline_copy)
        # Init git in baseline if missing (so measure_git doesn't error)
        if not (baseline_copy / ".git").exists():
            run(["git", "init", "-q"], cwd=baseline_copy)
            run(["git", "add", "-A"], cwd=baseline_copy)
            run(["git", "commit", "-m", "baseline", "-q",
                 "--allow-empty"], cwd=baseline_copy,
                env={"GIT_AUTHOR_NAME": "grader", "GIT_AUTHOR_EMAIL": "g@g",
                     "GIT_COMMITTER_NAME": "grader", "GIT_COMMITTER_EMAIL": "g@g"})

        baseline_result = measure_repo(baseline_copy, "baseline")
        workspace_result = measure_repo(args.workspace, "workspace")

    # Compute deltas
    def safe_sub(a, b):
        if a is None or b is None: return None
        return a - b

    bp = baseline_result["pytest"]
    wp = workspace_result["pytest"]
    deltas = {
        "passed": safe_sub(wp["passed"], bp["passed"]),
        "total_tests": safe_sub(wp["total"], bp["total"]),
        "pass_rate": safe_sub(wp["pass_rate"], bp["pass_rate"]),
        "line_coverage_pct": safe_sub(workspace_result["coverage"]["line_coverage_pct"],
                                      baseline_result["coverage"]["line_coverage_pct"]),
        "ruff_issues": safe_sub(workspace_result["ruff"]["issue_count"],
                                baseline_result["ruff"]["issue_count"]),
        "benchmark_seconds": safe_sub(workspace_result["benchmark"]["elapsed_s"],
                                      baseline_result["benchmark"]["elapsed_s"]),
        "py_file_count": safe_sub(workspace_result["files"]["py_file_count"],
                                  baseline_result["files"]["py_file_count"]),
        "experimental_py_deleted": (
            baseline_result["files"]["experimental_py_present"] and
            not workspace_result["files"]["experimental_py_present"]
        ),
        "agent_commits": workspace_result["git"]["commit_count"],
    }

    result = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "baseline": baseline_result,
        "workspace": workspace_result,
        "deltas": deltas,
    }
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(deltas, indent=2))


if __name__ == "__main__":
    main()
