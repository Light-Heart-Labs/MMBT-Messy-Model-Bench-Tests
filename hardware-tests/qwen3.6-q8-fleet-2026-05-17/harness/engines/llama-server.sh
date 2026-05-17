#!/usr/bin/env bash
# llama-server.sh — start a llama-server for the bench, host+backend-aware.
# Picks the right build-<backend>/bin/llama-server. Sets env so output is
# captured. Idempotent: refuses to start if a server is already on the port.
#
# Usage:
#   llama-server.sh start <backend> <model_path> <port> <ctx> <parallel> [extra_flags...]
#   llama-server.sh stop  <port>
#   llama-server.sh wait-ready <port> <timeout_s>
#
# Backends: cuda-tower2 | cuda-spark | rocm | vulkan | metal
# Each maps to ${BENCH_LLAMA_DIR}/build-<backend>/bin/llama-server.

set -euo pipefail

BENCH_LLAMA_DIR="${BENCH_LLAMA_DIR:-$HOME/bench-fleet-llama-cpp}"

cmd_start() {
    local backend="$1" model="$2" port="$3" ctx="$4" parallel="$5"; shift 5
    # bash 3.2 (default on macOS) errors on "${extra[@]}" when empty under set -u.
    # The `${arr[@]+...}` form is the bash-3.2-safe way to expand only-if-set.
    local extra=("$@")
    # silence "unused" warning when no extra args; expansion handled below.
    : "${extra[@]+set}"
    local bin="$BENCH_LLAMA_DIR/build-$backend/bin/llama-server"
    [[ -x "$bin" ]] || { echo "missing $bin" >&2; exit 2; }
    [[ -f "$model" ]] || { echo "missing model $model" >&2; exit 2; }

    if curl -fsS --max-time 1 "http://127.0.0.1:$port/health" >/dev/null 2>&1; then
        echo "llama-server already running on port $port" >&2
        exit 3
    fi

    # Tower2 GPU pinning: only GPU 0 (breaker-safe parallel run).
    if [[ "$backend" == "cuda-tower2" ]]; then
        export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
    fi

    local logdir="${BENCH_LOG_DIR:-/tmp/bench-fleet}"
    mkdir -p "$logdir"
    local log="$logdir/llama-server-$port.log"

    # Force all layers to GPU (-ngl 99) and disable the auto-fit pass — the
    # auto-fitter can spend 5+ min probing layouts on unified-memory hosts.
    # `-fa auto` lets each backend use FA if it supports it (recorded in cell metadata).
    nohup "$bin" \
        --model "$model" \
        --ctx-size "$ctx" \
        --parallel "$parallel" \
        --port "$port" \
        --host 127.0.0.1 \
        --n-gpu-layers 99 \
        --no-warmup \
        --jinja \
        --metrics \
        -fa auto \
        -fit off \
        ${extra[@]+"${extra[@]}"} \
        > "$log" 2>&1 &
    echo "$!"
}

cmd_wait_ready() {
    local port="$1" timeout="$2"
    local deadline=$(( $(date +%s) + timeout ))
    while (( $(date +%s) < deadline )); do
        if curl -fsS --max-time 2 "http://127.0.0.1:$port/health" 2>/dev/null | grep -q '"status":"ok"'; then
            echo "ready"
            return 0
        fi
        sleep 2
    done
    echo "timeout waiting for port $port" >&2
    return 1
}

cmd_stop() {
    local port="$1"
    local pid
    pid="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
    if [[ -n "$pid" ]]; then
        kill "$pid" 2>/dev/null || true
        for _ in {1..15}; do
            kill -0 "$pid" 2>/dev/null || break
            sleep 1
        done
        kill -9 "$pid" 2>/dev/null || true
    fi
}

case "${1:-}" in
    start)      shift; cmd_start "$@" ;;
    wait-ready) shift; cmd_wait_ready "$@" ;;
    stop)       shift; cmd_stop "$@" ;;
    *)          echo "usage: $0 {start|wait-ready|stop} ..." >&2; exit 2 ;;
esac
