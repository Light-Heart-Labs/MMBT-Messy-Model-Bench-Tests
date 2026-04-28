#!/usr/bin/env python3
"""Phase 1 grader wrapper — runs code_task_grader on a delivered workspace
and adds task-specific pass/fail scoring on top.

Tasks supported:
- bugfix:    pass = pytest pass-rate increased AND ruff issues didn't regress AND benchmark didn't regress materially
- testwrite: pass = coverage % increased AND baseline tests still pass AND no production-code changes (only /tests/ may differ)
- refactor:  pass = baseline tests still pass AND output/ subpackage structure created AND non-output files unchanged AND old imports still work

Usage:
  phase1_grade.py <task> <workspace_dir> <baseline_dir> [--out grade.json]

  task = bugfix | testwrite | refactor
  workspace_dir = the agent's delivered repo (extracted from workspace_final.tar.gz)
  baseline_dir = the logalyzer starter
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


THIS_DIR = Path(__file__).resolve().parent
CORE_GRADER = THIS_DIR / "code_task_grader.py"


def run(cmd, cwd=None, timeout=120, check=False):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed ({p.returncode}): {cmd}\n{p.stderr}")
    return p


def grade_bugfix(workspace: Path, baseline: Path) -> dict:
    """Bug-fix task: pytest pass-rate up, ruff issues not worse, bench not regressed."""
    # Run the core grader to get all metrics
    out = workspace / ".grade.json"
    r = run(["python3", str(CORE_GRADER),
             "--workspace", str(workspace),
             "--baseline", str(baseline),
             "--out", str(out)], timeout=900)
    if not out.exists():
        return {"task": "bugfix", "verdict": "GRADER_FAILED", "notes": r.stderr[-500:]}
    metrics = json.loads(out.read_text())
    # Extract the deltas
    bef_pass = metrics.get("baseline", {}).get("pytest", {}).get("passed", 0)
    bef_total = metrics.get("baseline", {}).get("pytest", {}).get("total", 0)
    aft_pass = metrics.get("workspace", {}).get("pytest", {}).get("passed", 0)
    aft_total = metrics.get("workspace", {}).get("pytest", {}).get("total", 0)
    bef_cov = metrics.get("baseline", {}).get("coverage_pct")
    aft_cov = metrics.get("workspace", {}).get("coverage_pct")
    bef_ruff = metrics.get("baseline", {}).get("ruff_issues", 0)
    aft_ruff = metrics.get("workspace", {}).get("ruff_issues", 0)
    bef_bench = metrics.get("baseline", {}).get("benchmark_s")
    aft_bench = metrics.get("workspace", {}).get("benchmark_s")
    # Pass criteria
    pass_rate_improved = (aft_pass - bef_pass) > 0
    ruff_no_regression = aft_ruff <= bef_ruff
    bench_no_major_regression = (
        aft_bench is None or bef_bench is None
        or aft_bench <= bef_bench * 1.10  # allow 10% slowdown
    )
    verdict = (
        "PASS" if (pass_rate_improved and ruff_no_regression and bench_no_major_regression)
        else "FAIL"
    )
    return {
        "task": "bugfix",
        "verdict": verdict,
        "criteria": {
            "pass_rate_improved": pass_rate_improved,
            "ruff_no_regression": ruff_no_regression,
            "bench_no_major_regression": bench_no_major_regression,
        },
        "before": {"passed": bef_pass, "total": bef_total, "cov": bef_cov, "ruff": bef_ruff, "bench_s": bef_bench},
        "after": {"passed": aft_pass, "total": aft_total, "cov": aft_cov, "ruff": aft_ruff, "bench_s": aft_bench},
        "delta": {"passed": aft_pass - bef_pass, "cov": (aft_cov - bef_cov) if (bef_cov and aft_cov) else None,
                  "ruff": aft_ruff - bef_ruff, "bench_s": (aft_bench - bef_bench) if (bef_bench and aft_bench) else None},
    }


def grade_testwrite(workspace: Path, baseline: Path) -> dict:
    """Test-writing task: coverage up, baseline tests still pass, /logalyzer/ unchanged."""
    out = workspace / ".grade.json"
    r = run(["python3", str(CORE_GRADER),
             "--workspace", str(workspace),
             "--baseline", str(baseline),
             "--out", str(out)], timeout=900)
    if not out.exists():
        return {"task": "testwrite", "verdict": "GRADER_FAILED", "notes": r.stderr[-500:]}
    metrics = json.loads(out.read_text())
    bef_pass = metrics.get("baseline", {}).get("pytest", {}).get("passed", 0)
    aft_pass = metrics.get("workspace", {}).get("pytest", {}).get("passed", 0)
    aft_total = metrics.get("workspace", {}).get("pytest", {}).get("total", 0)
    bef_cov = metrics.get("baseline", {}).get("coverage_pct") or 0
    aft_cov = metrics.get("workspace", {}).get("coverage_pct") or 0
    # Check that /logalyzer/ is byte-identical between baseline and workspace
    diff_r = run(["diff", "-r", str(baseline / "logalyzer"), str(workspace / "logalyzer")], timeout=30)
    logalyzer_unchanged = diff_r.returncode == 0
    # Pass criteria
    coverage_improved = (aft_cov - bef_cov) > 1.0  # >1pp improvement
    baseline_tests_pass = aft_pass >= bef_pass  # no regressions
    verdict = (
        "PASS" if (coverage_improved and baseline_tests_pass and logalyzer_unchanged)
        else "FAIL"
    )
    return {
        "task": "testwrite",
        "verdict": verdict,
        "criteria": {
            "coverage_improved": coverage_improved,
            "baseline_tests_pass": baseline_tests_pass,
            "logalyzer_unchanged": logalyzer_unchanged,
        },
        "before": {"cov": bef_cov, "passed": bef_pass},
        "after": {"cov": aft_cov, "passed": aft_pass, "total": aft_total},
        "delta": {"cov_pp": round(aft_cov - bef_cov, 1)},
    }


def grade_refactor(workspace: Path, baseline: Path) -> dict:
    """Refactor task: baseline tests still pass, output/ subpackage exists, old imports work,
    non-output files unchanged."""
    # Run pytest in workspace to verify behavior preservation
    pyt = run(["python3", "-m", "pytest", "-q", "--tb=no", "--no-header"],
              cwd=workspace, timeout=180)
    out = pyt.stdout + "\n" + pyt.stderr
    import re
    m = re.search(r"(\d+) passed", out)
    aft_pass = int(m.group(1)) if m else 0
    pyt_b = run(["python3", "-m", "pytest", "-q", "--tb=no", "--no-header"],
                cwd=baseline, timeout=180)
    out_b = pyt_b.stdout + "\n" + pyt_b.stderr
    m_b = re.search(r"(\d+) passed", out_b)
    bef_pass = int(m_b.group(1)) if m_b else 0
    # Structural check 1: output/ subpackage exists
    output_pkg = workspace / "logalyzer" / "output"
    output_pkg_exists = output_pkg.is_dir()
    output_renderers = []
    for fname in ["json_renderer.py", "csv_renderer.py", "plain_renderer.py", "legacy.py"]:
        if (output_pkg / fname).is_file():
            output_renderers.append(fname)
    # Structural check 2: old output.py is gone or empty
    old_output = workspace / "logalyzer" / "output.py"
    old_output_gone = not old_output.is_file()
    # Structural check 3: backward-compat import works
    import_check = run(["python3", "-c",
                        "from logalyzer.output import format_legacy; print('ok')"],
                       cwd=workspace, timeout=30)
    backward_compat = import_check.returncode == 0 and "ok" in import_check.stdout
    # Structural check 4: non-output files in /logalyzer/ are unchanged
    non_output_changed = []
    for f in ["parser.py", "cli.py", "filters.py", "io.py", "utils.py", "experimental.py", "aggregate.py", "__init__.py"]:
        bf = baseline / "logalyzer" / f
        wf = workspace / "logalyzer" / f
        if bf.is_file() and wf.is_file():
            if bf.read_bytes() != wf.read_bytes():
                non_output_changed.append(f)
        elif bf.is_file() and not wf.is_file():
            non_output_changed.append(f"{f} (deleted)")
    # /tests/ unchanged
    tests_diff = run(["diff", "-rq", str(baseline / "tests"), str(workspace / "tests")], timeout=30)
    tests_unchanged = tests_diff.returncode == 0
    # Pass criteria
    tests_pass = aft_pass >= bef_pass
    structure_correct = output_pkg_exists and len(output_renderers) >= 3  # at least 3 of the 4
    verdict = (
        "PASS" if (tests_pass and structure_correct and backward_compat
                   and len(non_output_changed) == 0 and tests_unchanged)
        else "FAIL"
    )
    return {
        "task": "refactor",
        "verdict": verdict,
        "criteria": {
            "tests_pass": tests_pass,
            "output_pkg_exists": output_pkg_exists,
            "output_renderers_present": output_renderers,
            "old_output_gone": old_output_gone,
            "backward_compat_import": backward_compat,
            "non_output_files_unchanged": len(non_output_changed) == 0,
            "tests_unchanged": tests_unchanged,
        },
        "before": {"passed": bef_pass},
        "after": {"passed": aft_pass},
        "non_output_changed": non_output_changed,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("task", choices=["bugfix", "testwrite", "refactor"])
    ap.add_argument("workspace", help="path to extracted agent workspace")
    ap.add_argument("baseline", help="path to logalyzer starter")
    ap.add_argument("--out", default=None, help="output path for grade.json (default: <workspace>/grade.json)")
    args = ap.parse_args()

    workspace = Path(args.workspace).resolve()
    baseline = Path(args.baseline).resolve()
    if not workspace.is_dir():
        ap.error(f"workspace not a dir: {workspace}")
    if not baseline.is_dir():
        ap.error(f"baseline not a dir: {baseline}")

    if args.task == "bugfix":
        result = grade_bugfix(workspace, baseline)
    elif args.task == "testwrite":
        result = grade_testwrite(workspace, baseline)
    elif args.task == "refactor":
        result = grade_refactor(workspace, baseline)

    out_path = Path(args.out) if args.out else (workspace / "grade.json")
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
