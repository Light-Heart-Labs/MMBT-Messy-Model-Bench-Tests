#!/usr/bin/env bash
# Run conc=1 single-user grid on M5 via MLX.
set -uo pipefail
MODEL_PATH="${1:-/Users/conta/models/mlx/Qwen3.6-27B-8bit}"
PROMPTS="${2:-$HOME/mlx-bench/prompts.jsonl}"
OUT_BASE="${3:-$HOME/mlx-bench/results}"
N_BATCHES="${4:-10}"
WARMUP="${5:-2}"

mkdir -p "$OUT_BASE"
ts="$(date -u +%FT%TZ)"
LOG="$OUT_BASE/run-$ts.log"
echo "[$ts] starting MLX grid model=$MODEL_PATH out=$OUT_BASE" | tee "$LOG"

for ctx in 1024 4096 16384 32768; do
    for gen in 128 512 2048; do
        cell="ctx$(printf '%05d' "$ctx")_gen$(printf '%04d' "$gen")_conc1"
        out="$OUT_BASE/$cell"
        mkdir -p "$out"
        if [[ -f "$out/.done" ]]; then
            echo "[$(date -u +%FT%TZ)] skip $cell (.done present)" | tee -a "$LOG"
            continue
        fi
        echo "[$(date -u +%FT%TZ)] >>> cell $cell" | tee -a "$LOG"
        if $HOME/mlx-bench/.venv/bin/python $HOME/mlx-bench/bench-cell-mlx.py \
                --model-path "$MODEL_PATH" --prompts "$PROMPTS" \
                --ctx "$ctx" --gen "$gen" --conc 1 \
                --n-batches "$N_BATCHES" --warmup-batches "$WARMUP" \
                --out "$out" 2>&1 | tee "$out/bench-cell.log" >> "$LOG"; then
            : # driver creates .done
        else
            echo "bench-cell-failed" > "$out/.error"
            echo "  CELL FAILED $cell" | tee -a "$LOG"
        fi
    done
done
echo "[$(date -u +%FT%TZ)] grid done" | tee -a "$LOG"
