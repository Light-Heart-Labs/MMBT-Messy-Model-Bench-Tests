#!/usr/bin/env bash
# sustained-host.sh — 30-min continuous decode at a fixed cell, for thermal-
# throttle characterization. Runs on the target host directly.
#
# Strategy:
#   1) Launch llama-server at <ctx, parallel> as a long-lived process
#   2) Start power + thermal samplers (1Hz)
#   3) Issue back-to-back /completion requests for <duration_s> seconds,
#      tracking decode_tps per request and timestamps
#   4) Stop samplers + server, write summary
#
# Per-request prompt = same as bench-host (deterministic, fixed seed).

set -euo pipefail

BACKEND="" MODEL="" GRID="" PROMPTS="" OUT=""
SAMPLER_POWER="" SAMPLER_THERMAL=""
POWER_PROBE="" THERMAL_PROBE="" ENGINE_HELPER=""
CTX=4096 GEN=512 CONC=1 DURATION_S=1800

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
        --ctx)             CTX="$2"; shift 2 ;;
        --gen)             GEN="$2"; shift 2 ;;
        --conc)            CONC="$2"; shift 2 ;;
        --duration)        DURATION_S="$2"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

mkdir -p "$OUT"
log() { printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

PORT_BASE="${BENCH_PORT_BASE:-19000}"
port=$((PORT_BASE + RANDOM % 1000))
while lsof -ti tcp:"$port" >/dev/null 2>&1; do port=$((port + 1)); done

CTX_TOTAL=$(( CTX * CONC + 1024 ))
log "sustained start: backend=$BACKEND ctx=$CTX gen=$GEN conc=$CONC duration=${DURATION_S}s port=$port"

# Reuse the same single prompt every request (deterministic).
# Note: don't use `| head -1` because SIGPIPE on jq + `set -e pipefail` aborts;
# use `[0]` slice in jq to grab first match inline.
prompt="$(jq -sc --argjson ctx "$CTX" --argjson gen "$GEN" \
    'map(select(.context_target == $ctx and .gen_target == $gen) | .prompt) | .[0]' \
    "$PROMPTS")"
[[ -n "$prompt" && "$prompt" != "null" ]] || { echo "no matching prompt for ctx=$CTX gen=$GEN" >&2; exit 2; }

server_pid="$(BENCH_LOG_DIR="$OUT" "$ENGINE_HELPER" start "$BACKEND" "$MODEL" "$port" "$CTX_TOTAL" "$CONC")"
log "  server pid=$server_pid"
"$ENGINE_HELPER" wait-ready "$port" 300 >/dev/null || { log "  server-timeout"; exit 1; }

"$POWER_PROBE"   "$OUT/power.csv"    "$SAMPLER_POWER"   &  pwr_pid=$!
"$THERMAL_PROBE" "$OUT/thermals.csv" "$SAMPLER_THERMAL" &  thm_pid=$!

results="$OUT/inferences.jsonl"
: > "$results"

deadline=$(( $(date +%s) + DURATION_S ))
idx=0
while (( $(date +%s) < deadline )); do
    idx=$((idx+1))
    t0="$(date +%s.%N)"
    body="$(curl -sS --max-time 600 -X POST "http://127.0.0.1:$port/completion" \
        -H 'Content-Type: application/json' \
        -d "$(jq -n --arg p "$prompt" --argjson n "$GEN" \
            '{prompt:$p, n_predict:$n, temperature:0, seed:42, cache_prompt:false, stream:false}')" 2>/dev/null)"
    t1="$(date +%s.%N)"
    [[ -z "$body" ]] && continue
    decode="$(jq -r '.timings.predicted_per_second // 0' <<<"$body")"
    prefill="$(jq -r '.timings.prompt_per_second // 0' <<<"$body")"
    ttft="$(jq -r '.timings.prompt_ms // 0' <<<"$body")"
    gen_tok="$(jq -r '.timings.predicted_n // 0' <<<"$body")"
    jq -nc --argjson idx "$idx" --arg t0 "$t0" --arg t1 "$t1" \
          --argjson decode "$decode" --argjson prefill "$prefill" \
          --argjson ttft "$ttft" --argjson gtok "$gen_tok" \
          '{idx:$idx, t0:($t0|tonumber), t1:($t1|tonumber),
            decode_tps:$decode, prefill_tps:$prefill, ttft_ms:$ttft, gen_tokens:$gtok}' \
          >> "$results"
    if (( idx % 10 == 0 )); then
        log "  progress idx=$idx remaining=$((deadline - $(date +%s)))s last_decode_tps=$decode"
    fi
done

kill "$pwr_pid" "$thm_pid" 2>/dev/null || true
wait "$pwr_pid" "$thm_pid" 2>/dev/null || true
"$ENGINE_HELPER" stop "$port" || true

# Summary stratified by minute, so we can see throttle curves
jq -s --argjson dur "$DURATION_S" '
    sort_by(.t0)
    | (.[0].t0) as $t0
    | map(. + {minute: ((.t0 - $t0) / 60 | floor)})
    | group_by(.minute)
    | map({minute: .[0].minute,
           n: length,
           decode_tps_mean: (map(.decode_tps) | add / length),
           decode_tps_min:  (map(.decode_tps) | min),
           decode_tps_max:  (map(.decode_tps) | max)})
    | {duration_s: $dur, minutes: .}' "$results" > "$OUT/per-minute.json"

log "sustained done: $idx inferences in ${DURATION_S}s"
