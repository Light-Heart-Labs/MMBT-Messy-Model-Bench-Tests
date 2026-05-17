#!/usr/bin/env bash
# bench-host-v2.sh — run the bench grid for ONE (host, model, backend).
# Improvements over v1:
#   G1: each cell's artifacts ready before the next cell starts (atomic-on-disk)
#   G2: cell.meta.json captures host env + server cmdline + backend version
#   G3: true-parallel concurrency via bench-cell.py (asyncio)
#   G4: cold-start surfaced explicitly in cell.json
#   G5: env snapshot written once at start (env.json)
#
# Required args (same as v1) plus:
#   --notify-script <path>   optional script invoked with the cell dir after each
#                            cell completes. Used by the orchestrator to rsync +
#                            commit per cell.

set -euo pipefail

BACKEND="" MODEL="" GRID="" PROMPTS="" OUT=""
SAMPLER_POWER="" SAMPLER_THERMAL=""
POWER_PROBE="" THERMAL_PROBE="" ENGINE_HELPER=""
NOTIFY_SCRIPT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --backend)         BACKEND="$2"; shift 2 ;;
        --model)           MODEL="$2"; shift 2 ;;
        --grid)            GRID="$2"; shift 2 ;;
        --prompts)         PROMPTS="$2"; shift 2 ;;
        --out)             OUT="$2"; shift 2 ;;
        --sampler-power)   SAMPLER_POWER="$2"; shift 2 ;;
        --sampler-thermal) SAMPLER_THERMAL="$2"; shift 2 ;;
        --power-probe)     POWER_PROBE="$2"; shift 2 ;;
        --thermal-probe)   THERMAL_PROBE="$2"; shift 2 ;;
        --engine-helper)   ENGINE_HELPER="$2"; shift 2 ;;
        --notify-script)   NOTIFY_SCRIPT="$2"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

for v in BACKEND MODEL GRID PROMPTS OUT SAMPLER_POWER SAMPLER_THERMAL POWER_PROBE THERMAL_PROBE ENGINE_HELPER; do
    [[ -n "${!v}" ]] || { echo "missing --${v,,}" >&2; exit 2; }
done

mkdir -p "$OUT"
log() { printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

# Parent-side SIGTERM/SIGINT cleanup: when bench-host itself is killed (eg by
# orchestrator pause), its grandchildren (llama-server, bench-cell.py, probes)
# reparent to init and the next run leaks state. Wipe our whole process group
# (and the engine helper's idea of "running server") before exiting.
# Without this trap, "pause then resume" leaks orphan llama-servers + samplers,
# observed during the 2026-05-16 pause.
_cleanup_parent() {
    local sig="${1:-EXIT}"
    log "bench-host parent received $sig — killing process group"
    pkill -P $$ -KILL 2>/dev/null || true
    if [[ -n "${ENGINE_HELPER:-}" && -x "$ENGINE_HELPER" ]]; then
        "$ENGINE_HELPER" stop-all 2>/dev/null || true
    fi
    pkill -KILL -f "probe-power.sh|probe-thermals.sh|bench-cell.py|bench-cell-vllm" 2>/dev/null || true
    exit 130
}
trap '_cleanup_parent SIGTERM' SIGTERM
trap '_cleanup_parent SIGINT'  SIGINT

CONTEXTS=( $(jq -r '.contexts[]'      "$GRID") )
GENS=(     $(jq -r '.gen_lengths[]'   "$GRID") )
CONCS=(    $(jq -r '.concurrencies[]' "$GRID") )
N_PER_CELL="$(jq -r '.n_per_cell' "$GRID")"
WARMUP="$(jq -r '.warmup_discard' "$GRID")"

PORT_BASE="${BENCH_PORT_BASE:-19000}"

# ----- env snapshot once at start -----
SCRIPT_DIR_BH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_JSON="$OUT/env.json"
log "snapshotting host environment to $ENV_JSON"
{
    echo "{"
    echo "  \"hostname\":     \"$(hostname)\","
    echo "  \"os\":           \"$(uname -s)\","
    echo "  \"kernel\":       \"$(uname -r)\","
    echo "  \"arch\":         \"$(uname -m)\","
    echo "  \"date_started\": \"$(date -u +%FT%TZ)\","
    echo "  \"backend\":      \"$BACKEND\","
    echo "  \"model\":        \"$MODEL\","
    # Try to capture each backend's identifying info
    case "$BACKEND" in
        cuda-tower2|cuda-spark)
            echo "  \"nvidia_smi\":   \"$(nvidia-smi --query-gpu=name,driver_version,memory.total,power.limit --format=csv,noheader 2>/dev/null | head -1 | tr -d '"')\","
            echo "  \"nvcc_version\": \"$(nvcc --version 2>/dev/null | tail -1 | tr -d '"')\","
            ;;
        rocm)
            echo "  \"rocm_version\": \"$(cat /opt/rocm/.info/version 2>/dev/null || echo unknown)\","
            echo "  \"radeon_card\":  \"$(rocm-smi --showproductname 2>/dev/null | grep -i 'Card series' | head -1 | tr -d '"')\","
            ;;
        vulkan)
            echo "  \"vulkan_devices\": \"$(vulkaninfo --summary 2>/dev/null | grep deviceName | head -2 | tr -d '"\t' | sed 's/^[[:space:]]*//' | tr '\n' ';')\","
            ;;
        metal)
            echo "  \"macos_version\":  \"$(sw_vers -productVersion 2>/dev/null)\","
            echo "  \"metal_sdk\":      \"$(xcrun --sdk macosx --show-sdk-version 2>/dev/null)\","
            echo "  \"hw_model\":       \"$(sysctl -n hw.model 2>/dev/null)\","
            echo "  \"cpu_brand\":      \"$(sysctl -n machdep.cpu.brand_string 2>/dev/null)\","
            ;;
    esac
    echo "  \"cmake_version\":   \"$(cmake --version 2>/dev/null | head -1)\","
    echo "  \"build_dir\":       \"build-$BACKEND\","
    echo "  \"llama_bin\":       \"$(echo "${BENCH_LLAMA_DIR:-$HOME/bench-fleet-llama-cpp}/build-$BACKEND/bin/llama-server")\""
    echo "}"
} > "$ENV_JSON"

cell_dir() {
    local ctx="$1" gen="$2" conc="$3"
    printf '%s/ctx%05d_gen%04d_conc%d' "$OUT" "$ctx" "$gen" "$conc"
}

run_cell() {
    local ctx="$1" gen="$2" conc="$3"
    local dir; dir="$(cell_dir "$ctx" "$gen" "$conc")"
    mkdir -p "$dir"

    if [[ -f "$dir/.done" ]]; then
        log "skip cell ctx=$ctx gen=$gen conc=$conc (already done)"
        [[ -n "$NOTIFY_SCRIPT" ]] && "$NOTIFY_SCRIPT" "$dir" >/dev/null 2>&1 || true
        return 0
    fi

    log "=== cell ctx=$ctx gen=$gen conc=$conc ==="
    local port=$((PORT_BASE + RANDOM % 1000))
    while lsof -ti tcp:"$port" >/dev/null 2>&1; do port=$((port + 1)); done

    local ctx_total=$(( ctx * conc + 1024 ))
    local server_pid
    server_pid="$(BENCH_LOG_DIR="$dir" "$ENGINE_HELPER" start "$BACKEND" "$MODEL" "$port" "$ctx_total" "$conc")"
    log "  llama-server pid=$server_pid port=$port ctx_total=$ctx_total"

    if ! "$ENGINE_HELPER" wait-ready "$port" 600 >/dev/null; then
        log "  FAIL: server didn't become ready"
        "$ENGINE_HELPER" stop "$port" >/dev/null 2>&1 || true
        echo "server-timeout" > "$dir/.error"
        return 1
    fi

    # G2: parse server log header into cell.meta.json
    local srvlog="$dir/llama-server-$port.log"
    if [[ -f "$srvlog" ]]; then
        local fa_resolved llama_build_str
        fa_resolved="$(grep -m1 -iE "flash.attn|fa.*=|attention.*flash" "$srvlog" | head -1 | tr -d '"' || true)"
        llama_build_str="$(grep -m1 -iE "build [0-9]+|^build " "$srvlog" | head -1 | tr -d '"' || true)"
        cat > "$dir/cell.meta.json" <<EOF
{
  "backend": "$BACKEND",
  "ctx": $ctx, "gen": $gen, "conc": $conc,
  "model_path": "$MODEL",
  "ctx_size_total": $ctx_total,
  "parallel_slots": $conc,
  "n_gpu_layers": 99,
  "flash_attention": "$fa_resolved",
  "llama_build": "$llama_build_str",
  "wait_ready_used_s": "captured",
  "server_log": "llama-server-$port.log"
}
EOF
    fi

    # Start samplers
    "$POWER_PROBE"   "$dir/power.csv"    "$SAMPLER_POWER"   &  local pwr_pid=$!
    "$THERMAL_PROBE" "$dir/thermals.csv" "$SAMPLER_THERMAL" &  local thm_pid=$!

    # G3: hand off to bench-cell.py for true parallel issue
    local bench_cell="$(dirname "$0")/bench-cell.py"
    if ! python3 "$bench_cell" \
            --host 127.0.0.1 --port "$port" \
            --prompts "$PROMPTS" \
            --ctx "$ctx" --gen "$gen" --conc "$conc" \
            --n-batches "$N_PER_CELL" --warmup-batches "$WARMUP" \
            --out "$dir" 2>&1 | tee -a "$dir/bench-cell.log"; then
        log "  bench-cell.py failed"
        echo "bench-cell-failed" > "$dir/.error"
    fi

    # Kill the probe wrappers AND their children. Critical on macOS where
    # `kill <pid>` to the bash wrapper does NOT propagate through the macmon|python
    # pipeline — the macmon child survives as an orphan and bench-host hangs in `wait`.
    # Also critical on Linux where probe-thermals.sh's trap action can hit a
    # bash parse error and refuse to exit cleanly on SIGTERM (observed on Tower2
    # cuda-tower2 dual-card run, 2026-05-16) — SIGKILL escalation is the fix.
    pkill -P "$pwr_pid" 2>/dev/null || true
    pkill -P "$thm_pid" 2>/dev/null || true
    kill "$pwr_pid" "$thm_pid" 2>/dev/null || true
    # Belt-and-suspenders: nuke any stragglers writing to this cell's CSVs.
    pkill -f "macmon pipe -i 1000" 2>/dev/null || true
    # Brief grace period, then SIGKILL escalation if probes haven't exited yet
    sleep 1
    if kill -0 "$pwr_pid" 2>/dev/null; then
        pkill -KILL -P "$pwr_pid" 2>/dev/null || true
        kill -KILL "$pwr_pid" 2>/dev/null || true
    fi
    if kill -0 "$thm_pid" 2>/dev/null; then
        pkill -KILL -P "$thm_pid" 2>/dev/null || true
        kill -KILL "$thm_pid" 2>/dev/null || true
    fi
    wait "$pwr_pid" "$thm_pid" 2>/dev/null || true
    "$ENGINE_HELPER" stop "$port" || true

    if [[ -f "$dir/cell.json" && -f "$dir/.done" ]]; then
        local decode_mean; decode_mean="$(jq -r '.per_slot.decode_tps_mean // "—"' "$dir/cell.json" 2>/dev/null)"
        local agg_mean; agg_mean="$(jq -r '.aggregate.aggregate_decode_tps_mean // "—"' "$dir/cell.json" 2>/dev/null)"
        log "  cell done — per_slot_decode_mean=$decode_mean aggregate_decode_mean=$agg_mean"
    else
        log "  cell exited without producing cell.json/.done — see .error"
    fi

    # G1: notify the orchestrator that this cell is fully on disk
    if [[ -n "$NOTIFY_SCRIPT" ]]; then
        "$NOTIFY_SCRIPT" "$dir" >/dev/null 2>&1 || true
    fi
}

log "host bench start backend=$BACKEND model=$(basename "$MODEL")"
log "grid: ${#CONTEXTS[@]}c × ${#GENS[@]}g × ${#CONCS[@]}p × N=$N_PER_CELL"

for ctx in "${CONTEXTS[@]}"; do
  for gen in "${GENS[@]}"; do
    for conc in "${CONCS[@]}"; do
      run_cell "$ctx" "$gen" "$conc" || log "  cell error — continuing"
    done
  done
done

log "host bench done"
