#!/usr/bin/env bash
# bench-cell-vllm-probed.sh — wrap bench-cell-vllm.py with the same power+thermal
# probes that bench-host.sh uses for llama.cpp cells. Closes the audit gap where
# the original vLLM bench harness ran outside bench-host.sh and produced no
# sampler CSVs.
#
# Usage:
#   bench-cell-vllm-probed.sh <cell_dir> <ctx> <gen> <conc> <port> <n_batches> <warmup_batches>
#
# Output: <cell_dir>/{cell.json, batches.jsonl, inferences.jsonl, .done,
#                     power.csv, thermals.csv, bench-cell.log}

set -euo pipefail

CELL_DIR="${1:?cell_dir required}"
CTX="${2:?ctx required}"
GEN="${3:?gen required}"
CONC="${4:?conc required}"
PORT="${5:?port required}"
N="${6:-3}"
WARMUP="${7:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS=/home/michael/bench-fleet/workloads/prompts.jsonl
SAMPLER_POWER=nvidia-smi
SAMPLER_THERMAL='nvidia-smi+sensors'

mkdir -p "$CELL_DIR"

log() { printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

log "cell start ctx=$CTX gen=$GEN conc=$CONC N=$N (warmup=$WARMUP) port=$PORT"

# Start probes
"$SCRIPT_DIR/probe-power.sh"   "$CELL_DIR/power.csv"    "$SAMPLER_POWER"   &  pwr_pid=$!
"$SCRIPT_DIR/probe-thermals.sh" "$CELL_DIR/thermals.csv" "$SAMPLER_THERMAL" &  thm_pid=$!

# Probes need a moment to write their CSV header
sleep 0.5

# Run the cell
set +e
python3 "$SCRIPT_DIR/bench-cell-vllm.py" \
    --host 127.0.0.1 --port "$PORT" \
    --prompts "$PROMPTS" \
    --ctx "$CTX" --gen "$GEN" --conc "$CONC" \
    --n-batches "$N" --warmup-batches "$WARMUP" \
    --out "$CELL_DIR" 2>&1 | tee "$CELL_DIR/bench-cell.log"
rc=${PIPESTATUS[0]}
set -e

# Stop probes — explicit PIDs only, never pkill -f
kill -TERM "$pwr_pid" "$thm_pid" 2>/dev/null || true
wait "$pwr_pid" 2>/dev/null || true
wait "$thm_pid" 2>/dev/null || true

log "cell done rc=$rc"
exit $rc
