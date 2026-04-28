#!/usr/bin/env bash
# Run N=10 on the 4 differential microbench cells × 2 models.
# Bench-side script — generates p_<task>_<model>_v4..v10 (existing v1-v3 stay).
#
# Cells targeted: adversarial-hallucination, market-research, doc-synthesis,
# business-memo. These are the 4 cells where the microbench's headline
# claims about per-task-class differences come from. N=3 → N=10 buys us
# 95% Wilson CIs that distinguish 1/3 vs 3/3 (overlap [1%, 71%] vs
# [29%, 99%] at N=3 → 1/10 vs 10/10 has CIs [0%, 28%] vs [72%, 100%], no
# overlap).
#
# Total: 4 cells × 2 models × 7 additional reps = 56 runs.
#
# IMPORTANT: --stuck-threshold 100 for doc-synthesis-27B specifically.
# That cell is known to identical-call-loop on brief.md after producing
# the 763-775-word draft. With threshold 500 each loop run is 2-5 hours
# wall; with 100 it's ~10 min. Saves 6+ hours over 7 runs.
#
# Usage: bash agent-pilot/scripts/run_diff_cells_n10.sh
# Run from ~/bench/. Assumes vLLM endpoints already up (27B port 8000,
# Coder-Next port 8001 per the canonical launch-commands.md).

set -e

BENCH="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$BENCH"

# Sanity: both endpoints reachable
echo "==> Checking vLLM endpoints..."
if ! curl -sf http://127.0.0.1:8000/v1/models >/dev/null; then
  echo "ERROR: 27B endpoint not reachable on port 8000"; exit 1
fi
if ! curl -sf http://127.0.0.1:8001/v1/models >/dev/null; then
  echo "ERROR: Coder-Next endpoint not reachable on port 8001"; exit 1
fi
echo "    OK"

# Cell config: name | task_file | input_dir | stuck_threshold_27b | stuck_threshold_coder
CELLS=(
  "hallucination|task_hallucination.md|agent-pilot/inputs/phase2_hallucination|500|500"
  "business|task_business_memo.md|agent-pilot/inputs/phase3_business_memo|500|500"
  "doc|task_doc_synthesis.md|agent-pilot/inputs/phase3_doc_synthesis|100|500"
  "market|task_market_research.md||500|500"
)

# Generate v4..v10 for each (model, cell)
START_T=$(date +%s)
COUNTER=0
TOTAL=$((${#CELLS[@]} * 2 * 7))

for entry in "${CELLS[@]}"; do
  IFS='|' read -r short task_file input_dir stuck_27b stuck_coder <<< "$entry"
  for model_pair in "27b|qwen3.6-27b-awq|8000|$stuck_27b" "coder|qwen3-coder-next-awq|8001|$stuck_coder"; do
    IFS='|' read -r model_label model_name port stuck_thresh <<< "$model_pair"
    for v in 4 5 6 7 8 9 10; do
      COUNTER=$((COUNTER + 1))
      run_name="p${short:0:1}_${short}_${model_label}_v${v}"
      # Phase prefix: hallucination/business/doc/market → p2/p3/p3/p3
      case "$short" in
        hallucination) run_name="p2_hallucination_${model_label}_v${v}" ;;
        business)      run_name="p3_business_${model_label}_v${v}" ;;
        doc)           run_name="p3_doc_${model_label}_v${v}" ;;
        market)        run_name="p3_market_${model_label}_v${v}" ;;
      esac

      # Skip if already done
      if [ -f "agent-pilot/logs/${run_name}/summary.json" ] && \
         [ -f "agent-pilot/logs/${run_name}/workspace_final.tar.gz" ]; then
        echo "[$COUNTER/$TOTAL] SKIP $run_name (already complete)"
        continue
      fi

      INPUT_FLAG=""
      [ -n "$input_dir" ] && INPUT_FLAG="--input-mount $input_dir"

      echo "[$COUNTER/$TOTAL] $run_name (stuck-threshold $stuck_thresh)  $(date +%H:%M:%S)"
      python3 agent-pilot/harness.py \
        "$run_name" \
        "agent-pilot/$task_file" \
        --model "$model_name" \
        --port "$port" \
        --temperature 0.3 \
        --stuck-threshold "$stuck_thresh" \
        $INPUT_FLAG \
        --docker-socket \
        --gpus all 2>&1 | tail -3 || echo "  WARN: harness exited non-zero"
    done
  done
done

ELAPSED=$(( $(date +%s) - START_T ))
H=$(( ELAPSED / 3600 )); M=$(( (ELAPSED % 3600) / 60 ))
echo ""
echo "==> Diff-cells N=10 chain complete"
echo "    elapsed: ${H}h${M}m"
echo "    next: bash agent-pilot/scripts/batch_grade_p3.sh && bash agent-pilot/scripts/batch_grade_p2.sh"
