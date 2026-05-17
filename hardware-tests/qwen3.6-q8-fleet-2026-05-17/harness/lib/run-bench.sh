#!/usr/bin/env bash
# run-bench.sh — invoke bench-host.sh on a single (host, model, backend) tuple.
# Streams results back as each cell completes (incremental rsync + per-cell git commit).
#
# Args: <host> <model_name> <backend> <run_dir>

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

HOST="${1:?usage: run-bench.sh <host> <model_name> <backend> <run_dir>}"
MODEL_NAME="${2:?}"
BACKEND="${3:?}"
RUN_DIR="${4:?}"

USER_HOME="$(target_field "$HOST" user_home)"
SSH_ALIAS="$(target_field "$HOST" ssh_alias)"
IS_LOCAL="$(target_field "$HOST" local)"
MODELS_DIR="$(target_field "$HOST" models_dir)"
LLAMA_DIR="$(target_field "$HOST" llama_cpp_dir)"
SAMPLER_POWER="$(target_field "$HOST" power_sampler)"
SAMPLER_THERMAL="$(target_field "$HOST" thermal_sampler)"

case "$BACKEND" in
    cuda)
        case "$HOST" in
            tower2) backend_suffix="cuda-tower2" ;;
            spark)  backend_suffix="cuda-spark"  ;;
            *) die "unknown cuda host $HOST" ;;
        esac
        ;;
    cuda-aarch64) backend_suffix="cuda-spark" ;;
    rocm)         backend_suffix="rocm" ;;
    vulkan)       backend_suffix="vulkan" ;;
    metal)        backend_suffix="metal" ;;
    *) die "unknown backend $BACKEND" ;;
esac
build_dir="build-$backend_suffix"

MODEL_FILE="$(jq -r --arg n "$MODEL_NAME" '.study.models[] | select(.name == $n) | .filename' "$TARGETS_JSON")"
[[ -n "$MODEL_FILE" ]] || die "unknown model name: $MODEL_NAME"
MODEL_PATH="$MODELS_DIR/$MODEL_FILE"

OUT_BASE="$RUN_DIR/$HOST/$MODEL_NAME/$BACKEND"
mkdir -p "$OUT_BASE"
log "host=$HOST model=$MODEL_NAME backend=$BACKEND -> $OUT_BASE"

REMOTE_BF="$USER_HOME/bench-fleet"
POWER_PROBE="$REMOTE_BF/lib/probe-power.sh"
THERMAL_PROBE="$REMOTE_BF/lib/probe-thermals.sh"
ENGINE_HELPER="$REMOTE_BF/engines/llama-server.sh"
BENCH_HOST="$REMOTE_BF/lib/bench-host.sh"

# Resolve grid + prompts (smoke vs full)
GRID_BASENAME="$(basename "${BENCH_GRID_OVERRIDE:-grid.json}")"
PROMPTS_BASENAME="$(basename "${BENCH_PROMPTS_OVERRIDE:-prompts.jsonl}")"
GRID="$REMOTE_BF/workloads/$GRID_BASENAME"
PROMPTS="$REMOTE_BF/workloads/$PROMPTS_BASENAME"

REMOTE_OUT="/tmp/bench-fleet-out-$HOST-$MODEL_NAME-$BACKEND-$$"
host_exec "$HOST" "rm -rf $REMOTE_OUT && mkdir -p $REMOTE_OUT" >/dev/null

# ---- Live watcher: every 30s, pull cells back + git-commit any new cell.json ----
watcher_pid=""
if [[ "$IS_LOCAL" != "true" ]]; then
    (
        set +e
        shopt -s nullglob
        while true; do
            sleep 30
            rsync -a --exclude='llama-server-*.log' \
                  "$SSH_ALIAS:$REMOTE_OUT/" "$OUT_BASE/" >/dev/null 2>&1 || true
            # Find newly-finished cells (those with .done) and commit them.
            for cell in "$OUT_BASE"/ctx*conc*/.done; do
                cdir="$(dirname "$cell")"
                rel="${cdir#$BENCH_FLEET_ROOT/}"
                marker="$cdir/.committed"
                if [[ ! -f "$marker" ]]; then
                    git -C "$BENCH_FLEET_ROOT" add \
                        "$rel/cell.json" "$rel/cell.meta.json" \
                        "$rel/inferences.jsonl" "$rel/batches.jsonl" \
                        "$rel/.done" 2>/dev/null || true
                    if ! git -C "$BENCH_FLEET_ROOT" diff --cached --quiet 2>/dev/null; then
                        git -C "$BENCH_FLEET_ROOT" \
                            -c user.name="bench-fleet" -c user.email="bench-fleet@local" \
                            commit -q -m "$HOST/$MODEL_NAME/$BACKEND: cell $(basename "$cdir")" 2>/dev/null || true
                    fi
                    touch "$marker"
                fi
            done
        done
    ) &
    watcher_pid=$!
fi

# ---- Run bench on the remote host ----
log "  starting remote bench-host.sh"
set +e
host_exec "$HOST" "BENCH_LLAMA_DIR=$LLAMA_DIR $BENCH_HOST \
    --backend $backend_suffix \
    --model $(printf %q "$MODEL_PATH") \
    --grid $GRID \
    --prompts $PROMPTS \
    --out $REMOTE_OUT \
    --sampler-power '$SAMPLER_POWER' \
    --sampler-thermal '$SAMPLER_THERMAL' \
    --power-probe $POWER_PROBE \
    --thermal-probe $THERMAL_PROBE \
    --engine-helper $ENGINE_HELPER" \
    > "$OUT_BASE/bench-host.log" 2>&1
rc=$?
set -e
log "  bench-host.sh rc=$rc"

# ---- Stop watcher + final rsync + final commit ----
if [[ -n "$watcher_pid" ]]; then
    kill "$watcher_pid" 2>/dev/null || true
    wait "$watcher_pid" 2>/dev/null || true
fi

if [[ "$IS_LOCAL" == "true" ]]; then
    cp -r "$REMOTE_OUT"/. "$OUT_BASE"/ 2>/dev/null || true
else
    rsync -a "$SSH_ALIAS:$REMOTE_OUT/" "$OUT_BASE/" >/dev/null 2>&1 || true
fi
host_exec "$HOST" "rm -rf $REMOTE_OUT" >/dev/null 2>&1 || true

# Final commit: anything not yet committed (server logs, env.json, power CSVs, etc.)
rel_base="${OUT_BASE#$BENCH_FLEET_ROOT/}"
git -C "$BENCH_FLEET_ROOT" add "$rel_base/" 2>/dev/null || true
if ! git -C "$BENCH_FLEET_ROOT" diff --cached --quiet 2>/dev/null; then
    git -C "$BENCH_FLEET_ROOT" \
        -c user.name="bench-fleet" -c user.email="bench-fleet@local" \
        commit -q -m "$HOST/$MODEL_NAME/$BACKEND: end-of-host artifacts" 2>/dev/null || true
fi

log "  results in $OUT_BASE/"
exit $rc
