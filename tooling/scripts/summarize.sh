#!/usr/bin/env bash
# Print a per-task PASS/FAIL summary table for one model's microbench results.
# Optionally compares against the canonical Coder-Next + 27B published numbers.
#
# Usage: bash tooling/scripts/summarize.sh <model-label>
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <model-label>"
  echo "Example: $0 llama3-70b"
  exit 1
fi

LABEL="$1"
TOOLING="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$TOOLING/.." && pwd)"

cd "$REPO_ROOT"

python3 << EOF
import json
from pathlib import Path
import statistics

logs = Path("logs")
label = "$LABEL"

# Reference numbers from the published microbench (Coder-Next + 27B at N=3)
REFERENCE = {
    "p1_bugfix":       {"27b": "3/3", "coder": "2/3"},
    "p1_testwrite":    {"27b": "0/3 †", "coder": "0/3 †"},
    "p1_refactor":     {"27b": "0/3 †", "coder": "0/3 †"},
    "p2_extract":      {"27b": "3/3", "coder": "3/3"},
    "p2_ci":           {"27b": "3/3", "coder": "3/3"},
    "p2_hallucination":{"27b": "3/3", "coder": "1/3"},
    "p2_triage":       {"27b": "3/3", "coder": "3/3"},
    "p3_doc":          {"27b": "0/3", "coder": "2/3"},
    "p3_business":     {"27b": "2/3", "coder": "3/3"},
    "p3_market":       {"27b": "3/3*", "coder": "0/3"},
    "p3_writing":      {"27b": "0/3", "coder": "2/3"},
    "p3_pm":           {"27b": "0/3", "coder": "1/3"},
}

# Collect this model's results
data = {}
for d in sorted(logs.glob(f"p[1-3]_*_{label}_v*/")):
    run = d.name
    # Extract task prefix
    parts = run.rsplit(f"_{label}_v", 1)
    if len(parts) != 2:
        continue
    prefix = parts[0]
    grade_p = d / "grade.json"
    cost_p = d / "cost.json"
    summary_p = d / "summary.json"

    verdict = "?"
    if grade_p.exists():
        verdict = json.loads(grade_p.read_text()).get("verdict", "?")

    cost = wall = None
    if cost_p.exists():
        c = json.loads(cost_p.read_text())
        cost = c.get("energy_estimate", {}).get("cost_usd_upper_bound")
        wall = c.get("wall_s")

    data.setdefault(prefix, []).append({"run": run, "verdict": verdict, "cost": cost, "wall": wall})

if not data:
    print(f"No runs found for label '{label}' in logs/")
    print(f"Did you run: bash tooling/scripts/run_microbench.sh <model> <port> {label}")
    raise SystemExit(2)

print(f"Microbench results for: {label}")
print()
print(f"{'task':<22} {'pass':<8} {'cost_med':<10} {'wall_med':<10} | {'27B (ref)':<10} {'Coder (ref)':<10}")
print("-" * 95)

total_pass = total_runs = 0
for prefix in [
    "p1_bugfix","p1_testwrite","p1_refactor",
    "p2_extract","p2_ci","p2_hallucination","p2_triage",
    "p3_doc","p3_business","p3_market","p3_writing","p3_pm",
]:
    if prefix not in data:
        ref = REFERENCE.get(prefix, {})
        print(f"{prefix:<22} {'(none)':<8} {'-':<10} {'-':<10} | {ref.get('27b','-'):<10} {ref.get('coder','-'):<10}")
        continue
    runs = data[prefix]
    passes = sum(1 for r in runs if r["verdict"] in ("PASS", "STRUCTURAL_PASS"))
    total = len(runs)
    total_pass += passes
    total_runs += total

    costs = [r["cost"] for r in runs if isinstance(r["cost"], (int, float))]
    walls = [r["wall"] for r in runs if isinstance(r["wall"], (int, float))]
    cost_str = f"\${statistics.median(costs):.4f}" if costs else "-"
    wall_str = f"{statistics.median(walls)/60:.1f}m" if walls else "-"

    ref = REFERENCE.get(prefix, {})
    print(f"{prefix:<22} {passes}/{total:<6} {cost_str:<10} {wall_str:<10} | {ref.get('27b','-'):<10} {ref.get('coder','-'):<10}")

print()
print(f"Total: {total_pass}/{total_runs} PASS")
print()
print("Reference numbers (Coder-Next, 27B): from microbench-2026-04-28 published results.")
print("† test-writing/refactoring affected by a starter-code task-design issue. See KNOWN-LIMITATIONS.md.")
print("* market-research is graded as STRUCTURAL_PASS — citation validity is hand-grading dimension.")
EOF
