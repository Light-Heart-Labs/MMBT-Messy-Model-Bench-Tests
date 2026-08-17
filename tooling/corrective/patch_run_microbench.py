#!/usr/bin/env python3
"""Surgical, idempotent patch of tooling/scripts/run_microbench.sh (Phase A).

Two default-preserving additions:
  1. BENCH_TASK_ONLY optional family allowlist (unset = unchanged behavior).
  2. Idempotent-resume skip check also accepts the automated terminal labels
     loop-run30 / timeout (automated: true), alongside the historical
     operator label identical-call-loop.

Exact-match replacement; refuses to run if the anchors are not found
byte-identically (so it can never silently corrupt the script).
"""

import sys
from pathlib import Path

path = Path(sys.argv[1] if len(sys.argv) > 1 else
            Path(__file__).resolve().parent.parent / "scripts" / "run_microbench.sh")
text = path.read_text()

MARKER = "BENCH_TASK_ONLY"
if MARKER in text:
    print(f"already patched: {path}")
    sys.exit(0)

# ---- anchor 1: after the TASKS array, add the optional family filter ----
anchor1 = '''  "p3_pm|task_project_mgmt.md|tooling/inputs/phase3_project_mgmt"
)

TOTAL_RUNS=$(( ${#TASKS[@]} * N ))'''

replacement1 = '''  "p3_pm|task_project_mgmt.md|tooling/inputs/phase3_project_mgmt"
)

# Optional corrective-campaign filter: run only the named task families.
# BENCH_TASK_ONLY is a comma-separated allowlist of task_short names
# (e.g. "p2_extract" or "p1_bugfix,p3_pm"). Unset/empty runs all families —
# historical behavior unchanged. Unknown names fail fast.
if [ -n "${BENCH_TASK_ONLY:-}" ]; then
  IFS=',' read -ra BENCH_TASK_WANT <<< "$BENCH_TASK_ONLY"
  for w in "${BENCH_TASK_WANT[@]}"; do
    found=0
    for entry in "${TASKS[@]}"; do
      [ "${entry%%|*}" = "$w" ] && found=1
    done
    if [ "$found" != "1" ]; then
      echo "ERROR: BENCH_TASK_ONLY names unknown task family: $w" >&2
      exit 2
    fi
  done
  FILTERED_TASKS=()
  for entry in "${TASKS[@]}"; do
    for w in "${BENCH_TASK_WANT[@]}"; do
      [ "${entry%%|*}" = "$w" ] && FILTERED_TASKS+=("$entry")
    done
  done
  TASKS=("${FILTERED_TASKS[@]}")
fi

TOTAL_RUNS=$(( ${#TASKS[@]} * N ))'''

# ---- anchor 2: terminal-label skip check --------------------------------
anchor2 = '''    if [ -f "logs/${run_name}/receipt.json" ] && \\
       [ -f "logs/${run_name}/transcript.jsonl" ] && \\
       [ -f "logs/${run_name}/label.json" ] && \\
       python3 -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("primary") == "identical-call-loop" else 1)' \\
         "logs/${run_name}/label.json"
    then
      echo "[$DONE/$TOTAL_RUNS] SKIP $run_name (operator-labeled terminal pathology)"'''

replacement2 = '''    if [ -f "logs/${run_name}/receipt.json" ] && \\
       [ -f "logs/${run_name}/transcript.jsonl" ] && \\
       [ -f "logs/${run_name}/label.json" ] && \\
       python3 -c 'import json,sys
lab = json.load(open(sys.argv[1]))
p = lab.get("primary")
terminal = p == "identical-call-loop" or (lab.get("automated") is True and p in ("loop-run30", "timeout"))
sys.exit(0 if terminal else 1)' \\
         "logs/${run_name}/label.json"
    then
      echo "[$DONE/$TOTAL_RUNS] SKIP $run_name (terminal-labeled pathology)"'''

for name, anchor, replacement in (("task-filter", anchor1, replacement1),
                                  ("label-skip", anchor2, replacement2)):
    if anchor not in text:
        print(f"ERROR: {name} anchor not found byte-identically in {path}; "
              f"refusing to patch", file=sys.stderr)
        sys.exit(1)
    if text.count(anchor) != 1:
        print(f"ERROR: {name} anchor is not unique in {path}", file=sys.stderr)
        sys.exit(1)
    text = text.replace(anchor, replacement)

path.write_text(text)
print(f"patched: {path}")
