#!/usr/bin/env bash
# prepare-host.sh — push the bench harness to a remote host and verify state.
# Called by run.sh once per host before bench/smoke phases.
#
# Pushes ~/bench-fleet/{lib,engines,workloads,targets.json} to the host's
# ~/bench-fleet/. Verifies the binaries built and the model SHA matches.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

HOST="${1:?usage: prepare-host.sh <host>}"

log "prepare $HOST"
USER_HOME="$(target_field "$HOST" user_home)"
SSH_ALIAS="$(target_field "$HOST" ssh_alias)"
IS_LOCAL="$(target_field "$HOST" local)"
MODELS_DIR="$(target_field "$HOST" models_dir)"
LLAMA_DIR="$(target_field "$HOST" llama_cpp_dir)"
BACKENDS_LIST="$(target_backends "$HOST")"

REMOTE_BF="$USER_HOME/bench-fleet"

# 1) Push harness (excluding results/ and model files)
if [[ "$IS_LOCAL" == "true" ]]; then
    log "  local host; skipping rsync"
else
    log "  rsync harness -> $HOST:$REMOTE_BF"
    rsync -a --delete \
        --exclude='results/' --exclude='.git/' --exclude='*.gguf' \
        "$BENCH_FLEET_ROOT/" "$SSH_ALIAS:$REMOTE_BF/"
fi

# 2) Verify model files (SHA-pin per study.models)
log "  verifying model SHAs"
n_models="$(jq '.study.models | length' "$TARGETS_JSON")"
for i in $(seq 0 $((n_models - 1))); do
    fname="$(jq -r ".study.models[$i].filename" "$TARGETS_JSON")"
    want="$(jq -r ".study.models[$i].sha256" "$TARGETS_JSON")"
    got="$(host_sha256 "$HOST" "$MODELS_DIR/$fname")"
    if [[ "$got" != "$want" ]]; then
        die "SHA mismatch on $HOST for $fname: want $want got $got"
    fi
    log "    ✓ $fname sha=${want:0:12}"
done

# 3) Verify each backend's binary exists
for backend in $BACKENDS_LIST; do
    # Map backend to build dir name (Tower2 CUDA uses cuda-tower2, Spark uses cuda-spark)
    case "$backend" in
        cuda)
            case "$HOST" in
                tower2) build_dir="build-cuda-tower2" ;;
                spark)  build_dir="build-cuda-spark"  ;;
                *)      build_dir="build-cuda" ;;
            esac
            ;;
        cuda-aarch64) build_dir="build-cuda-spark" ;;
        rocm)         build_dir="build-rocm" ;;
        vulkan)       build_dir="build-vulkan" ;;
        metal)        build_dir="build-metal" ;;
        *) die "unknown backend $backend for host $HOST" ;;
    esac
    bin="$LLAMA_DIR/$build_dir/bin/llama-server"
    if ! host_exec "$HOST" "test -x $(printf %q "$bin")" >/dev/null 2>&1; then
        die "$HOST: missing $bin (build did not complete)"
    fi
    log "    ✓ $backend binary at $bin"
done

log "prepare $HOST OK"
