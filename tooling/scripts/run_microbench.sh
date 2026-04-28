#!/usr/bin/env bash
# Run the full microbench (12 task families × N=3 = 36 runs) against one model.
#
# Usage: bash tooling/scripts/run_microbench.sh <served-model-name> <port> <model-label> [<n>]
#
# Args:
#   served-model-name: must match what your vLLM endpoint exposes via /v1/models
#   port: vLLM endpoint port
#   model-label: short tag used in run names (e.g. "qwen2.5-72b" → run names like
#                p2_extract_qwen2.5-72b_v1). Avoid spaces and slashes.
#   n: number of runs per cell (default 3). 1 for quick sweep, 3 for canonical.
#
# Wall: 3-7 hours for N=3 on Tower2-class hardware. Probably ~6-15 hours on
# slower setups. Plan to run overnight.
#
# Output: logs/p[1-3]_<task>_<model-label>_v[1-N]/  per task family per replicate.
# After completion, run grade_microbench.sh + summarize.sh.

set -euo pipefail

if [ $# -lt 3 ]; then
  cat <<EOF
Usage: $0 <served-model-name> <port> <model-label> [<n>]

Runs 12 task families × N replicates against the model on the given vLLM endpoint.

Args:
  served-model-name  what vLLM advertises (e.g. qwen3-coder-next-awq, llama3.3-70b)
  port               vLLM endpoint port (e.g. 8001)
  model-label        short tag for run names (no spaces/slashes; e.g. coder, 27b, llama3-70b)
  n                  N per cell (default 3)

Example:
  $0 my-llama3-70b 8001 llama3-70b 3

Recommended workflow:
  1. bash tooling/scripts/smoke_test.sh <model> <port>     # 2-5 min
  2. bash tooling/scripts/run_microbench.sh ...            # 3-7 hours
  3. bash tooling/scripts/grade_microbench.sh <model-label>
  4. bash tooling/scripts/summarize.sh <model-label>
EOF
  exit 1
fi

MODEL="$1"
PORT="$2"
LABEL="$3"
N="${4:-3}"

TOOLING="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$TOOLING/.." && pwd)"
cd "$REPO_ROOT"

# Sanity: endpoint reachable
if ! curl -sf "http://127.0.0.1:${PORT}/v1/models" >/dev/null; then
  echo "ERROR: vLLM endpoint not reachable on port $PORT."
  exit 2
fi

# Task family → (task prompt file, input dir or "" for none)
# Format: "task_short_name|task_file|input_dir"
TASKS=(
  "p1_bugfix|task_code_adoption.md|"
  "p1_testwrite|task_test_writing.md|"
  "p1_refactor|task_refactoring.md|"
  "p2_extract|task_extraction.md|tooling/inputs/phase2_extraction"
  "p2_ci|task_ci_failure.md|tooling/inputs/phase2_ci_failure"
  "p2_hallucination|task_hallucination.md|tooling/inputs/phase2_hallucination"
  "p2_triage|task_triage.md|tooling/inputs/phase2_triage"
  "p3_doc|task_doc_synthesis.md|tooling/inputs/phase3_doc_synthesis"
  "p3_business|task_business_memo.md|tooling/inputs/phase3_business_memo"
  "p3_market|task_market_research.md|"
  "p3_writing|task_writing_editing.md|tooling/inputs/phase3_writing_editing"
  "p3_pm|task_project_mgmt.md|tooling/inputs/phase3_project_mgmt"
)

TOTAL_RUNS=$(( ${#TASKS[@]} * N ))
START_T=$(date +%s)

echo "==> Microbench chain: $TOTAL_RUNS runs (${#TASKS[@]} task families × N=$N)"
echo "    model:    $MODEL  (label: $LABEL)"
echo "    port:     $PORT"
echo "    started:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

DONE=0
SKIPPED=0
FAILED=0

for entry in "${TASKS[@]}"; do
  IFS='|' read -r task_short task_file input_dir <<< "$entry"
  for v in $(seq 1 "$N"); do
    run_name="${task_short}_${LABEL}_v${v}"
    DONE=$((DONE + 1))

    # Skip if already done (idempotent re-runs)
    if [ -f "logs/${run_name}/summary.json" ] && [ -f "logs/${run_name}/workspace_final.tar.gz" ]; then
      echo "[$DONE/$TOTAL_RUNS] SKIP $run_name (already complete)"
      SKIPPED=$((SKIPPED + 1))
      continue
    fi

    # Build flag set
    INPUT_FLAG=""
    [ -n "$input_dir" ] && INPUT_FLAG="--input-mount $input_dir"

    echo "[$DONE/$TOTAL_RUNS] $run_name  (started $(date +%H:%M:%S))"
    if python3 "$TOOLING/harness.py" \
      "$run_name" \
      "$TOOLING/tasks/$task_file" \
      --model "$MODEL" \
      --port "$PORT" \
      --temperature 0.3 \
      --stuck-threshold 500 \
      $INPUT_FLAG \
      --docker-socket \
      --gpus all 2>&1 | tail -3
    then
      :
    else
      echo "  WARN: harness exited non-zero for $run_name (check logs/${run_name}/)"
      FAILED=$((FAILED + 1))
    fi
  done
done

ELAPSED=$(( $(date +%s) - START_T ))
H=$(( ELAPSED / 3600 ))
M=$(( (ELAPSED % 3600) / 60 ))

echo ""
echo "==> Microbench chain complete"
echo "    total:    $TOTAL_RUNS runs"
echo "    skipped:  $SKIPPED (already complete from prior invocations)"
echo "    failed:   $FAILED (see logs/<run_name>/transcript.jsonl)"
echo "    elapsed:  ${H}h${M}m"
echo ""
echo "Next:"
echo "    bash $TOOLING/scripts/grade_microbench.sh $LABEL"
echo "    bash $TOOLING/scripts/summarize.sh $LABEL"
