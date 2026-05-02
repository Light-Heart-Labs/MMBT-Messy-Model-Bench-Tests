#!/usr/bin/env bash
# 27B-no-think full task-family grid at N=10.
#
# Adds a third arm to the 27B-thinking vs Coder-Next comparison: same 27B
# weights but with chat_template_kwargs={enable_thinking:false} so the model
# skips its <think>...</think> block. Tests whether the no-think regime is
# competitive with Coder-Next on speed AND on agentic-task quality (vs the
# headline N=3 grid where 27B-thinking and Coder-Next aggregate-tied at
# 56%/56%).
#
# Targets the same 12 families as the existing 27B-thinking baseline, so
# results line up cell-for-cell. Run names use suffix `_27b-nothink_v{1-10}`
# to keep them separate from the existing `_27b_v{1-10}` runs.
#
# Endpoint: vllm-qwen36-awq on port 8002 (same container as 27B Phase B
# resume; vLLM continuous-batches requests across both streams).
#
# Usage: bash agent-pilot/scripts/run_full_grid_27b_nothink.sh
# Run from ~/bench/.

set -e

MODEL_NAME="qwen3.6-27b-awq"
PORT=8002
MODEL_LABEL="27b-nothink"
N_REPS=10

BENCH="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$BENCH"

# Pre-flight
if ! curl -sf "http://127.0.0.1:${PORT}/v1/models" >/dev/null; then
  echo "ERROR: vLLM 27B endpoint not reachable on port $PORT"
  exit 2
fi

# 12 task families: prefix | task_file | input_dir (empty = no mount)
CELLS=(
  "p1_bugfix|task_code_adoption.md|agent-pilot/inputs/code-task-starter"
  "p1_refactor|task_refactoring.md|agent-pilot/inputs/code-task-starter"
  "p1_testwrite|task_test_writing.md|agent-pilot/inputs/code-task-starter"
  "p2_ci|task_ci_failure.md|agent-pilot/inputs/phase2_ci_failure"
  "p2_extract|task_extraction.md|agent-pilot/inputs/phase2_extraction"
  "p2_hallucination|task_hallucination.md|agent-pilot/inputs/phase2_hallucination"
  "p2_triage|task_triage.md|agent-pilot/inputs/phase2_triage"
  "p3_business|task_business_memo.md|agent-pilot/inputs/phase3_business_memo"
  "p3_doc|task_doc_synthesis.md|agent-pilot/inputs/phase3_doc_synthesis"
  "p3_market|task_market_research.md|"
  "p3_pm|task_project_mgmt.md|agent-pilot/inputs/phase3_project_mgmt"
  "p3_writing|task_writing_editing.md|agent-pilot/inputs/phase3_writing_editing"
)

START_T=$(date +%s)
COUNTER=0
TOTAL=$(( ${#CELLS[@]} * N_REPS ))

echo "==> 27B-no-think full grid — $MODEL_NAME on port $PORT"
echo "    cells: ${#CELLS[@]} × reps: $N_REPS = $TOTAL runs"
echo "    started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

for entry in "${CELLS[@]}"; do
  IFS='|' read -r cell_prefix task_file input_dir <<< "$entry"
  for v in $(seq 1 $N_REPS); do
    COUNTER=$((COUNTER + 1))
    run_name="${cell_prefix}_${MODEL_LABEL}_v${v}"

    if [ -f "agent-pilot/logs/${run_name}/summary.json" ] && \
       [ -f "agent-pilot/logs/${run_name}/workspace_final.tar.gz" ]; then
      echo "[$COUNTER/$TOTAL] SKIP $run_name (already complete)"
      continue
    fi

    INPUT_FLAG=""
    [ -n "$input_dir" ] && INPUT_FLAG="--input-mount $input_dir"

    echo "[$COUNTER/$TOTAL] $run_name  (started $(date +%H:%M:%S))"
    python3 agent-pilot/harness.py \
      "$run_name" \
      "agent-pilot/$task_file" \
      --model "$MODEL_NAME" \
      --port "$PORT" \
      --temperature 0.3 \
      --stuck-threshold 500 \
      $INPUT_FLAG \
      --no-think \
      --docker-socket \
      --gpus all 2>&1 | tail -3 || echo "  WARN: harness exited non-zero for $run_name"
  done
done

ELAPSED=$(( $(date +%s) - START_T ))
H=$(( ELAPSED / 3600 )); M=$(( (ELAPSED % 3600) / 60 ))
echo ""
echo "==> 27B-no-think full grid complete: ${H}h${M}m elapsed"
