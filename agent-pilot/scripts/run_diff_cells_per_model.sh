#!/usr/bin/env bash
# Run all 4 differential cells × 7 reps for ONE model. Designed to be
# launched twice (once per model) for parallel execution across both
# GPUs. Each invocation is independent; idempotency check (skip if
# summary.json + workspace_final.tar.gz exist) handles already-done runs.
#
# Methodology: identical harness flags to v1-v3 (--temperature 0.3
# --stuck-threshold 500 --docker-socket --gpus all). doc-synthesis-27B
# will identical-call-loop on brief.md; operator monitors and SIGTERMs
# manually when observed (matches v1-v3 manual-advance methodology).
#
# Usage: bash run_diff_cells_per_model.sh <27b|coder>
set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 <27b|coder>"
  exit 1
fi

MODEL_LABEL="$1"
case "$MODEL_LABEL" in
  27b)   MODEL_NAME="qwen3.6-27b-awq"; PORT=8000 ;;
  coder) MODEL_NAME="qwen3-coder-next-awq"; PORT=8001 ;;
  *)     echo "ERROR: unknown model label: $MODEL_LABEL"; exit 1 ;;
esac

BENCH="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$BENCH"

# Pre-flight
if ! curl -sf "http://127.0.0.1:${PORT}/v1/models" >/dev/null; then
  echo "ERROR: vLLM endpoint for $MODEL_LABEL not reachable on port $PORT"
  exit 2
fi

# 4 differential cells. Same task list / input mounts as v1-v3.
CELLS=(
  "p2_hallucination|task_hallucination.md|agent-pilot/inputs/phase2_hallucination"
  "p3_business|task_business_memo.md|agent-pilot/inputs/phase3_business_memo"
  "p3_doc|task_doc_synthesis.md|agent-pilot/inputs/phase3_doc_synthesis"
  "p3_market|task_market_research.md|"
)

START_T=$(date +%s)
COUNTER=0
TOTAL=$(( ${#CELLS[@]} * 7 ))

echo "==> Diff-cells N=10 chain — model: $MODEL_LABEL ($MODEL_NAME on port $PORT)"
echo "    cells: ${#CELLS[@]} × reps: 7 = $TOTAL runs"
echo "    started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

for entry in "${CELLS[@]}"; do
  IFS='|' read -r cell_prefix task_file input_dir <<< "$entry"
  for v in 4 5 6 7 8 9 10; do
    COUNTER=$((COUNTER + 1))
    run_name="${cell_prefix}_${MODEL_LABEL}_v${v}"

    # Skip if already done
    if [ -f "agent-pilot/logs/${run_name}/summary.json" ] && \
       [ -f "agent-pilot/logs/${run_name}/workspace_final.tar.gz" ]; then
      echo "[$COUNTER/$TOTAL][$MODEL_LABEL] SKIP $run_name (already complete)"
      continue
    fi

    INPUT_FLAG=""
    [ -n "$input_dir" ] && INPUT_FLAG="--input-mount $input_dir"

    echo "[$COUNTER/$TOTAL][$MODEL_LABEL] $run_name  (started $(date +%H:%M:%S))"
    python3 agent-pilot/harness.py \
      "$run_name" \
      "agent-pilot/$task_file" \
      --model "$MODEL_NAME" \
      --port "$PORT" \
      --temperature 0.3 \
      --stuck-threshold 500 \
      $INPUT_FLAG \
      --docker-socket \
      --gpus all 2>&1 | tail -3 || echo "  WARN: harness exited non-zero for $run_name"
  done
done

ELAPSED=$(( $(date +%s) - START_T ))
H=$(( ELAPSED / 3600 )); M=$(( (ELAPSED % 3600) / 60 ))
echo ""
echo "==> Chain $MODEL_LABEL complete: ${H}h${M}m elapsed"
