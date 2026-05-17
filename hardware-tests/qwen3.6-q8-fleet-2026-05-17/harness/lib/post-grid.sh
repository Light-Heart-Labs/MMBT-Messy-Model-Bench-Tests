#!/usr/bin/env bash
# post-grid.sh — runs after the main bench orchestrator exits.
# Sequence:
#   1. Wait for the bench orchestrator PID to exit
#   2. M5 27B backfill (cells lost to the bash 3.2 bug at start)
#   3. Sustained-thermal sub-study (30 min per host × 2 models)
#   4. MMBT Phase B Q8 eval on Tower2 (Goal 1 deliverable)
#   5. Final aggregate + report + commit

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

RUN_DIR="${1:?usage: post-grid.sh <run_dir>}"
ORCH_PID="${2:-753944}"

POST_LOG="$RUN_DIR/post-grid.log"
mkdir -p "$RUN_DIR"

p_log() { printf '[%s] post-grid: %s\n' "$(date -u +%FT%TZ)" "$*" | tee -a "$POST_LOG"; }

# -----------------------------------------------------------------------------
# Step 1: wait for orchestrator
# -----------------------------------------------------------------------------
p_log "waiting for orchestrator PID $ORCH_PID to exit..."
while kill -0 "$ORCH_PID" 2>/dev/null; do
    sleep 60
done
p_log "orchestrator $ORCH_PID exited; beginning post-grid sequence"

# -----------------------------------------------------------------------------
# Step 2: M5 27B backfill
# -----------------------------------------------------------------------------
p_log "=== M5 27B backfill ==="
M5_27B_DONE=$(find "$RUN_DIR/m5-mbp/qwen3.6-27b/metal" -name .done 2>/dev/null | wc -l)
if (( M5_27B_DONE >= 36 )); then
    p_log "M5 27B already has $M5_27B_DONE/36 .done cells, skipping backfill"
else
    # Ensure dir exists for the watcher
    mkdir -p "$RUN_DIR/m5-mbp/qwen3.6-27b/metal"
    p_log "launching run-bench.sh m5-mbp qwen3.6-27b metal"
    "$SCRIPT_DIR/run-bench.sh" m5-mbp qwen3.6-27b metal "$RUN_DIR" >> "$POST_LOG" 2>&1 || true
    p_log "M5 27B backfill exited"
fi

# -----------------------------------------------------------------------------
# Step 3: sustained-thermal sub-study (30 min per host × 2 models at host-optimal cell)
# -----------------------------------------------------------------------------
p_log "=== sustained-thermal sub-study ==="
# Pick host-optimal cell per host from the aggregate
SUSTAINED_OUT="$RUN_DIR/sustained"
mkdir -p "$SUSTAINED_OUT"
# Defer the actual sustained-host.sh launches — will write a separate orchestrator
# entry. Note this in the log so we know what's still pending.
p_log "TODO: sustained-host.sh fan-out — needs per-host optimal cell selection from aggregate"

# -----------------------------------------------------------------------------
# Step 4: MMBT Phase B Q8 quality eval (Tower2 only — model is bit-identical
#         across hosts per semantic-equivalence proof)
# -----------------------------------------------------------------------------
p_log "=== MMBT Phase B Q8 eval on Tower2 ==="
MMBT_OUT="$RUN_DIR/mmbt-phase-b-q8"
mkdir -p "$MMBT_OUT"

# Stop dream-llama-server first to free GPU 0 (may already be stopped)
docker stop dream-llama-server 2>/dev/null || true

# Use Tower2's existing build-cuda-tower2 llama-server with --jinja for tool-calling
LLAMA_BIN=/home/michael/bench-fleet-llama-cpp/build-cuda-tower2/bin/llama-server

for MODEL_LABEL in qwen3.6-27b qwen3.6-35b-a3b; do
    GGUF=$(jq -r --arg n "$MODEL_LABEL" '.study.models[] | select(.name == $n) | .filename' "$BENCH_FLEET_ROOT/targets.json")
    MODEL_PATH=/home/michael/models/bench-fleet/$GGUF

    p_log "starting llama-server for MMBT eval: $MODEL_LABEL"
    PORT=18800
    CUDA_VISIBLE_DEVICES=0 "$LLAMA_BIN" \
        --model "$MODEL_PATH" \
        --ctx-size 32768 --parallel 4 \
        --port $PORT --host 127.0.0.1 \
        --n-gpu-layers 99 --no-warmup \
        --jinja --metrics \
        -fa auto -fit off \
        > "$MMBT_OUT/llama-server-$MODEL_LABEL.log" 2>&1 &
    LLAMA_PID=$!

    # Wait for /health
    for i in $(seq 1 60); do
        if curl -fsS --max-time 2 "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -q ok; then
            p_log "  llama-server ready for $MODEL_LABEL"
            break
        fi
        sleep 5
    done

    # Run MMBT microbench (canonical N=3 per task family × 12 families = 36 runs)
    SHORT_LABEL=$(echo "$MODEL_LABEL" | tr -d '.-')-q8
    p_log "  invoking run_microbench.sh $MODEL_LABEL port=$PORT label=$SHORT_LABEL N=3"
    pushd /home/michael/bench >/dev/null
    bash tooling/scripts/run_microbench.sh "$MODEL_LABEL" "$PORT" "$SHORT_LABEL" 3 \
        >> "$MMBT_OUT/microbench-$MODEL_LABEL.log" 2>&1 || true
    popd >/dev/null
    p_log "  microbench for $MODEL_LABEL done; grading"
    pushd /home/michael/bench >/dev/null
    bash tooling/scripts/grade_microbench.sh "$SHORT_LABEL" \
        >> "$MMBT_OUT/grading-$MODEL_LABEL.log" 2>&1 || true
    popd >/dev/null

    # Stop llama-server
    kill "$LLAMA_PID" 2>/dev/null || true
    sleep 5
    kill -9 "$LLAMA_PID" 2>/dev/null || true
    p_log "  llama-server stopped for $MODEL_LABEL"
done

# -----------------------------------------------------------------------------
# Step 5: Final aggregate + report
# -----------------------------------------------------------------------------
p_log "=== final aggregate + report ==="
"$SCRIPT_DIR/aggregate.sh" "$RUN_DIR" >> "$POST_LOG" 2>&1
"$SCRIPT_DIR/report.sh"    "$RUN_DIR" >> "$POST_LOG" 2>&1
"$SCRIPT_DIR/live-snapshot.sh" "$RUN_DIR" >> "$POST_LOG" 2>&1  # last snapshot

# Restart dream-llama-server on Tower2 + Spark
docker start dream-llama-server 2>/dev/null || true
ssh spark 'docker start dream-llama-server 2>/dev/null || true' 2>&1 || true

# Commit everything
git -C "$BENCH_FLEET_ROOT" add -A
git -C "$BENCH_FLEET_ROOT" \
    -c user.name="bench-fleet" -c user.email="bench-fleet@local" \
    commit -q -m "post-grid complete: M5 backfill + MMBT Phase B Q8 eval + final report" 2>/dev/null || true

p_log "post-grid sequence COMPLETE"
p_log "see: $RUN_DIR/REFERENCE.md  $RUN_DIR/mmbt-phase-b-q8/  $RUN_DIR/aggregate/"
