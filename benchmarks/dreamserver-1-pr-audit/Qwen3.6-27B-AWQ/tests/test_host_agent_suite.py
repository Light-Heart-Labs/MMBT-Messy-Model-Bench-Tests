#!/usr/bin/env python3
"""Test that the host agent tests pass on both main and PR #1057.

Run with: python test_host_agent_suite.py
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2] / "dreamserver"
TEST_FILE = "dream-server/extensions/services/dashboard-api/tests/test_host_agent.py"

def run_tests(branch: str) -> tuple[int, int, str]:
    """Run pytest on the given branch. Returns (passed, failed, output)."""
    subprocess.run(["git", "checkout", branch], cwd=REPO, check=True,
                   capture_output=True)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", TEST_FILE, "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True
    )
    output = result.stdout
    # Parse results from last line
    last_line = output.strip().split("\n")[-1]
    passed = failed = 0
    for part in last_line.split():
        if part.endswith("passed"):
            passed = int(part)
        elif part.endswith("failed"):
            failed = int(part)
    return passed, failed, output

def main():
    print("=" * 60)
    print("Running host agent tests on main...")
    print("=" * 60)
    p1, f1, _ = run_tests("main")
    print(f"  Passed: {p1}, Failed: {f1}")

    print()
    print("=" * 60)
    print("Running host agent tests on PR #1057...")
    print("=" * 60)
    p2, f2, _ = run_tests("refs/pull/1057/head")
    print(f"  Passed: {p2}, Failed: {f2}")

    print()
    if f1 == 0 and f2 == 0:
        print("✅ All tests pass on both branches.")
    elif f2 > f1:
        print("❌ PR #1057 introduces regressions!")
        sys.exit(1)
    elif f1 > 0 and f2 == f1:
        print("⚠️  Tests fail on both branches (pre-existing failures).")
    else:
        print("⚠️  Unexpected result.")

if __name__ == "__main__":
    main()
