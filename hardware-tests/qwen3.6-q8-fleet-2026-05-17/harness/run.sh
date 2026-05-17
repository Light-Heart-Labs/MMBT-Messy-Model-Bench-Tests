#!/usr/bin/env bash
# run.sh — bench-fleet orchestrator.
#
# Usage: run.sh [--phase PHASE] [--hosts h1,h2] [--models m1,m2] [--backends b1,b2]
#               [--run-dir DIR]
#
# Phases:
#   prepare    rsync model files + build llama.cpp on every host (parallel)
#   smoke      one-cell validation on every host × model × backend
#   bench      full main-study grid
#   sustained  30-min sustained-thermal sub-study
#   bonus      Coder-Next on Blackwell hosts (Tower2 canonical, Spark attempted)
#   appendix   native-engine appendix (vLLM Tower2, MLX M5)
#   aggregate  merge per-host artifacts into cross-host pivot
#   report     render REFERENCE.md + plots
#   publish    open PR to MMBT
#   all        prepare → smoke → bench → sustained → aggregate → report (no bonus/appendix/publish by default)
#
# Default: --phase smoke, every host, every backend.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/lib/common.sh"

PHASE="smoke"
HOSTS_OVERRIDE=""
MODELS_OVERRIDE=""
BACKENDS_OVERRIDE=""
RUN_DIR=""
GRID_OVERRIDE=""
PROMPTS_OVERRIDE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --phase)    PHASE="$2"; shift 2 ;;
        --hosts)    HOSTS_OVERRIDE="$2"; shift 2 ;;
        --models)   MODELS_OVERRIDE="$2"; shift 2 ;;
        --backends) BACKENDS_OVERRIDE="$2"; shift 2 ;;
        --run-dir)  RUN_DIR="$2"; shift 2 ;;
        --grid)     GRID_OVERRIDE="$2"; shift 2 ;;
        --prompts)  PROMPTS_OVERRIDE="$2"; shift 2 ;;
        -h|--help)  sed -n '2,21p' "$0"; exit 0 ;;
        *)          die "unknown flag: $1" ;;
    esac
done

# Resolve run dir
if [[ -z "$RUN_DIR" ]]; then
    RUN_DIR="$BENCH_FLEET_ROOT/results/$(date -u +%Y-%m-%dT%H-%M-%SZ)"
fi
mkdir -p "$RUN_DIR"
log "RUN_DIR=$RUN_DIR"

# Resolve host list
if [[ -n "$HOSTS_OVERRIDE" ]]; then
    IFS=',' read -ra HOSTS <<< "$HOSTS_OVERRIDE"
else
    mapfile -t HOSTS < <(target_names)
fi
log "hosts: ${HOSTS[*]}"
log "phase: $PHASE"

# Resolve model + backend list per host
expand_targets() {
    # echo "host:model:backend" rows
    for h in "${HOSTS[@]}"; do
        local backends; backends="$(target_backends "$h")"
        local models
        if [[ -n "$MODELS_OVERRIDE" ]]; then
            IFS=',' read -ra models <<< "$MODELS_OVERRIDE"
        else
            mapfile -t models < <(jq -r '.study.models[].name' "$TARGETS_JSON")
        fi
        for m in "${models[@]}"; do
            for b in $backends; do
                if [[ -n "$BACKENDS_OVERRIDE" ]]; then
                    grep -q ",$b," <<< ",$BACKENDS_OVERRIDE," || continue
                fi
                echo "$h:$m:$b"
            done
        done
    done
}

phase_prepare() {
    local rc=0
    for h in "${HOSTS[@]}"; do
        log "=== prepare $h ==="
        if "$SCRIPT_DIR/lib/prepare-host.sh" "$h"; then
            log "    OK"
        else
            err "    FAILED"
            rc=1
        fi
    done
    return $rc
}

phase_smoke() {
    # Tiny grid by default; --grid/--prompts override.
    local grid="${GRID_OVERRIDE:-$BENCH_FLEET_ROOT/workloads/smoke-grid.json}"
    local prompts="${PROMPTS_OVERRIDE:-$BENCH_FLEET_ROOT/workloads/smoke-prompts.jsonl}"
    log "smoke grid=$grid prompts=$prompts"
    BENCH_GRID="$grid" BENCH_PROMPTS="$prompts" phase_bench
}

phase_bench() {
    # Run host-by-host serially through the prepared targets; each host runs
    # all of its (model, backend) sequentially. This implementation runs hosts
    # in parallel: we fan out one background job per host.
    declare -A pids
    declare -A logs
    for h in "${HOSTS[@]}"; do
        local hlog="$RUN_DIR/$h.log"
        mkdir -p "$RUN_DIR/$h"
        {
            for tuple in $(expand_targets | grep "^$h:"); do
                IFS=':' read -r host model backend <<< "$tuple"
                printf '[%s] starting %s/%s/%s\n' "$(date -u +%FT%TZ)" "$host" "$model" "$backend"
                BENCH_GRID_OVERRIDE="${BENCH_GRID:-}" \
                BENCH_PROMPTS_OVERRIDE="${BENCH_PROMPTS:-}" \
                "$SCRIPT_DIR/lib/run-bench.sh" "$host" "$model" "$backend" "$RUN_DIR" \
                    || printf '[%s] FAILED %s/%s/%s\n' "$(date -u +%FT%TZ)" "$host" "$model" "$backend"
            done
        } > "$hlog" 2>&1 &
        pids[$h]=$!
        logs[$h]="$hlog"
        log "  $h pid=${pids[$h]} log=$hlog"
    done

    local rc=0
    for h in "${HOSTS[@]}"; do
        if wait "${pids[$h]}"; then
            log "  $h done"
        else
            err "  $h failed (see ${logs[$h]})"
            rc=1
        fi
    done
    return $rc
}

phase_aggregate() { "$SCRIPT_DIR/lib/aggregate.sh" "$RUN_DIR"; }
phase_report()    { "$SCRIPT_DIR/lib/report.sh"    "$RUN_DIR"; }

case "$PHASE" in
    prepare)    phase_prepare ;;
    smoke)      phase_prepare && phase_smoke ;;
    bench)      phase_prepare && phase_bench ;;
    sustained)  die "sustained phase not yet wired (lib/sustained-host.sh exists)" ;;
    bonus)      die "bonus phase not yet wired" ;;
    appendix)   die "appendix phase not yet wired" ;;
    aggregate)  phase_aggregate ;;
    report)     phase_report ;;
    publish)    die "lib/publish.sh not yet implemented" ;;
    all)        phase_prepare && phase_bench && phase_aggregate && phase_report ;;
    *)          die "unknown phase: $PHASE" ;;
esac
