#!/usr/bin/env bash
# Smoke test: one quick task at N=1 to verify your vLLM endpoint + harness
# config work before you commit to a 3-7 hour full-microbench run.
#
# Usage: bash tooling/scripts/smoke_test.sh <served-model-name> <port> [<run-prefix>]
#
# Example: bash tooling/scripts/smoke_test.sh my-new-model 8001 smoke
#
# Exits 0 on PASS, non-zero otherwise. Wall: ~2-5 minutes.
set -euo pipefail

if [ $# -lt 2 ]; then
  cat <<EOF
Usage: $0 <served-model-name> <port> [<run-prefix>]

Runs the structured-extraction task at N=1 and grades it.
- structured-extraction is the fastest task (~30s-2min)
- It's also the most clearly-graded (per-field exact-match against ground truth)
- A PASS here means: vLLM endpoint works, tool-calling works, harness runs to completion, grader runs

Example:
  $0 qwen3-coder-next-awq 8001 smoke
EOF
  exit 1
fi

MODEL="$1"
PORT="$2"
PREFIX="${3:-smoke}"
TOOLING="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$TOOLING/.." && pwd)"
RUN_NAME="${PREFIX}_extract_$(date +%s)"

# Sanity: endpoint reachable?
echo "==> Checking vLLM endpoint at http://127.0.0.1:${PORT}/v1/models ..."
if ! curl -sf "http://127.0.0.1:${PORT}/v1/models" >/dev/null; then
  echo "ERROR: vLLM endpoint not reachable on port $PORT."
  echo "       Start vLLM first (see tooling/launch-commands.md)."
  exit 2
fi
echo "    OK"

# Sanity: the served model name matches?
if ! curl -sf "http://127.0.0.1:${PORT}/v1/models" | grep -q "\"$MODEL\""; then
  echo "WARN: served model name '$MODEL' not found in /v1/models response."
  echo "      Continuing anyway — vLLM accepts the model parameter as-is in most cases,"
  echo "      but if the run fails with 'model not found' from vLLM, double-check the"
  echo "      --served-model-name flag in your docker run."
fi

# Run the harness
echo ""
echo "==> Running smoke test: structured-extraction at N=1"
echo "    run_name=$RUN_NAME"
echo "    model=$MODEL  port=$PORT"
echo "    expected wall: 1-3 minutes"
echo ""

cd "$REPO_ROOT"
python3 "$TOOLING/harness.py" \
  "$RUN_NAME" \
  "$TOOLING/tasks/task_extraction.md" \
  --model "$MODEL" \
  --port "$PORT" \
  --temperature 0.3 \
  --stuck-threshold 500 \
  --input-mount "$TOOLING/inputs/phase2_extraction" \
  --docker-socket \
  --gpus all 2>&1 | tail -20

# Grade
echo ""
echo "==> Grading $RUN_NAME ..."
WORKSPACE="/tmp/grade_${RUN_NAME}"
mkdir -p "$WORKSPACE"
LOG_DIR="${REPO_ROOT}/logs/${RUN_NAME}"

if [ ! -f "${LOG_DIR}/workspace_final.tar.gz" ]; then
  echo "ERROR: ${LOG_DIR}/workspace_final.tar.gz not found."
  echo "       Harness probably failed mid-run. Check logs/${RUN_NAME}/transcript.jsonl"
  exit 3
fi

tar -xzf "${LOG_DIR}/workspace_final.tar.gz" -C "$WORKSPACE"
python3 "$TOOLING/graders/phase2_extraction_grade.py" \
  "$WORKSPACE" \
  "$TOOLING/graders/ground_truth/phase2_extraction.json" \
  --out "${LOG_DIR}/grade.json"

VERDICT=$(python3 -c "import json; print(json.load(open('${LOG_DIR}/grade.json')).get('verdict', '?'))")
ACCURACY=$(python3 -c "import json; d = json.load(open('${LOG_DIR}/grade.json')); print(d.get('scores', {}).get('field_accuracy', '?'))")

echo ""
echo "==> Smoke test result"
echo "    verdict:  $VERDICT"
echo "    accuracy: $ACCURACY"
echo "    log dir:  $LOG_DIR"
echo ""

if [ "$VERDICT" = "PASS" ]; then
  echo "✓ Smoke test PASS — your setup works. You can now run the full microbench:"
  echo ""
  echo "    bash $TOOLING/scripts/run_microbench.sh $MODEL $PORT <model-label>"
  echo ""
  exit 0
else
  echo "✗ Smoke test did not pass. Possible causes:"
  echo "  - Wrong --tool-call-parser flag for your model in vLLM (silent failure mode:"
  echo "    tool calls produce empty tool_calls arrays). Check transcript.jsonl for"
  echo "    'tcs=0' on every iter."
  echo "  - Wrong --reasoning-parser flag (output ends up in 'reasoning' field, not"
  echo "    'content'). Drop the flag for non-thinking models."
  echo "  - Model not strong enough on 20-field structured extraction. This task has"
  echo "    been 3/3 PASS on Qwen3.6-27B-AWQ and Qwen3-Coder-Next-AWQ at temp=0.3."
  echo "    Sub-7B-class models may legitimately fail here."
  echo "  - Harness config mismatch. Inspect logs/$RUN_NAME/summary.json for finish_reason."
  exit 1
fi
