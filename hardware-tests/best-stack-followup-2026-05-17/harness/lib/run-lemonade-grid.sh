#!/usr/bin/env bash
# Run the canonical 36-cell grid through a Lemonade Server.
# Reloads the model per (ctx, conc) combo so ctx_total fits the KV cache budget.

set -uo pipefail

MODEL="${1:-extra.Qwen3.6-27B-Q8_0.gguf}"
PROMPTS="${2:-$HOME/lemonade-bench/prompts.jsonl}"
OUT_BASE="${3:-$HOME/lemonade-bench/results}"
HOST="${4:-127.0.0.1}"
PORT="${5:-11434}"
N_BATCHES="${6:-10}"
WARMUP="${7:-2}"

mkdir -p "$OUT_BASE"
ts="$(date -u +%FT%TZ)"
LOG="$OUT_BASE/run-$ts.log"
echo "[$ts] starting lemonade grid model=$MODEL out=$OUT_BASE" | tee "$LOG"

for ctx in 1024 4096 16384 32768; do
    for conc in 1; do  # appendix scope: single-user only per user direction 2026-05-17
        # Per-request budget = prompt(ctx) + 2*gen_max + template buffer.
        # Lemonade reserves KV per request not per slot. Bumped from
        # ctx+2048+1024 → ctx+4096+2048 after observing "Context size exceeded"
        # errors at ctx=1024 gen=2048 with the tighter formula 2026-05-17.
        ctx_total=$(( ctx + 4096 + 2048 ))
        echo "[$(date -u +%FT%TZ)] === load ctx_size=$ctx_total (ctx=$ctx conc=$conc) ===" | tee -a "$LOG"
        load_resp=$(curl -sS -X POST "http://$HOST:$PORT/api/v1/load" \
            -H "Content-Type: application/json" \
            -d "{\"model_name\":\"$MODEL\",\"ctx_size\":$ctx_total}" 2>&1)
        echo "  load: $load_resp" | tee -a "$LOG"
        if ! echo "$load_resp" | grep -q '"status":"success"'; then
            echo "  LOAD FAILED — skipping cells for ctx=$ctx conc=$conc" | tee -a "$LOG"
            for gen in 128 512 2048; do
                cell="ctx$(printf '%05d' "$ctx")_gen$(printf '%04d' "$gen")_conc$conc"
                mkdir -p "$OUT_BASE/$cell"
                echo "load-failed-ctx$ctx_total" > "$OUT_BASE/$cell/.error"
            done
            continue
        fi
        for gen in 128 512 2048; do
            cell="ctx$(printf '%05d' "$ctx")_gen$(printf '%04d' "$gen")_conc$conc"
            out="$OUT_BASE/$cell"
            mkdir -p "$out"
            if [[ -f "$out/.done" ]]; then
                echo "[$(date -u +%FT%TZ)] skip $cell (.done present)" | tee -a "$LOG"
                continue
            fi
            echo "[$(date -u +%FT%TZ)] >>> cell $cell" | tee -a "$LOG"
            timeout=$(( 60 + gen * 4 ))
            if python3 "$HOME/lemonade-bench/bench-cell-lemonade.py" \
                    --host "$HOST" --port "$PORT" --model "$MODEL" \
                    --prompts "$PROMPTS" \
                    --ctx "$ctx" --gen "$gen" --conc "$conc" \
                    --n-batches "$N_BATCHES" --warmup-batches "$WARMUP" \
                    --timeout "$timeout" --out "$out" 2>&1 | tee "$out/bench-cell.log" >> "$LOG"; then
                : # bench-cell-lemonade.py creates .done on success
            else
                echo "bench-cell-failed" > "$out/.error"
                echo "  CELL FAILED $cell" | tee -a "$LOG"
            fi
        done
    done
done

echo "[$(date -u +%FT%TZ)] grid done" | tee -a "$LOG"
