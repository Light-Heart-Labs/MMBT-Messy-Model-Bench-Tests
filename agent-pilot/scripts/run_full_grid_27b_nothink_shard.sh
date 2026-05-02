#!/usr/bin/env bash
# Sharded variant of run_full_grid_27b_nothink.sh — designed to run two copies
# in parallel against two separate vLLM endpoints (one per GPU) after the
# Coder Phase B chain frees GPU1 for a second 27B vLLM.
#
# Each invocation handles a static subset of the 12 families × N=10 = 120 runs:
# run k (1-indexed across the full iteration) goes to shard ((k-1) mod
# SHARD_COUNT). With SHARD_COUNT=2, shard 0 gets odd reps and shard 1 gets
# even reps for every family — keeps load balanced across families even if
# some run faster than others.
#
# Usage: bash run_full_grid_27b_nothink_shard.sh <shard_id> <shard_count> <port>
#   shard_id: 0..(shard_count-1)
#   port:     vLLM endpoint port (8002 for GPU0 vllm-qwen36-awq;
#             8003 for GPU1 vllm-qwen36-awq-gpu1)

set -e

if [ $# -lt 3 ]; then
  echo "Usage: $0 <shard_id> <shard_count> <port>"
  exit 1
fi

SHARD_ID=$1
SHARD_COUNT=$2
PORT=$3
MODEL_NAME="qwen3.6-27b-awq"
MODEL_LABEL="27b-nothink"
N_REPS=10

if (( SHARD_ID < 0 || SHARD_ID >= SHARD_COUNT )); then
  echo "ERROR: shard_id $SHARD_ID out of range [0, $((SHARD_COUNT-1))]"
  exit 1
fi

BENCH="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$BENCH"

if ! curl -sf "http://127.0.0.1:${PORT}/v1/models" >/dev/null; then
  echo "ERROR: vLLM 27B endpoint not reachable on port $PORT"
  exit 2
fi

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
SHARD_COUNTER=0
TOTAL_THIS_SHARD=$(( ${#CELLS[@]} * N_REPS / SHARD_COUNT ))

echo "==> 27B-no-think SHARD $SHARD_ID/$SHARD_COUNT — $MODEL_NAME on port $PORT"
echo "    runs handled by this shard: ~$TOTAL_THIS_SHARD"
echo "    started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

for entry in "${CELLS[@]}"; do
  IFS='|' read -r cell_prefix task_file input_dir <<< "$entry"
  for v in $(seq 1 $N_REPS); do
    COUNTER=$((COUNTER + 1))
    if (( (COUNTER - 1) % SHARD_COUNT != SHARD_ID )); then
      continue
    fi
    SHARD_COUNTER=$((SHARD_COUNTER + 1))
    run_name="${cell_prefix}_${MODEL_LABEL}_v${v}"

    if [ -f "agent-pilot/logs/${run_name}/summary.json" ] && \
       [ -f "agent-pilot/logs/${run_name}/workspace_final.tar.gz" ]; then
      echo "[shard${SHARD_ID} $SHARD_COUNTER/$TOTAL_THIS_SHARD] SKIP $run_name (already complete)"
      continue
    fi

    # Defensive: if a sandbox with this run_name is already up (e.g., the other
    # shard or an orphan from a previous chain), skip rather than racing.
    if docker ps --filter name="bench-sandbox-${run_name}" -q | grep -q .; then
      echo "[shard${SHARD_ID} $SHARD_COUNTER/$TOTAL_THIS_SHARD] SKIP $run_name (sandbox already running, owned by other shard or orphan)"
      continue
    fi

    INPUT_FLAG=""
    [ -n "$input_dir" ] && INPUT_FLAG="--input-mount $input_dir"

    echo "[shard${SHARD_ID} $SHARD_COUNTER/$TOTAL_THIS_SHARD] $run_name  (started $(date +%H:%M:%S))"
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
echo "==> Shard $SHARD_ID/$SHARD_COUNT complete: ${H}h${M}m elapsed"
