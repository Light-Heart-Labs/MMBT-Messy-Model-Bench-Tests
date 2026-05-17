#!/usr/bin/env bash
# bench-host.sh — run the bench grid for ONE (host, model, backend) tuple.
# Designed to be invoked over SSH by the orchestrator. Writes per-cell artifacts
# into $OUT_DIR. Idempotent per cell (skips cells with an existing .done file).
#
# Required env / args:
#   --backend <id>     (cuda-tower2|cuda-spark|rocm|vulkan|metal)
#   --model   <path>   absolute path to .gguf on this host
#   --grid    <json>   path to grid.json
#   --prompts <jsonl>  path to prompts.jsonl
#   --out     <dir>    output dir (per-run, per-host, per-backend)
#   --sampler-power   (nvidia-smi|rocm-smi|powermetrics)
#   --sampler-thermal (nvidia-smi+sensors|rocm-smi+sensors|powermetrics)
#   --power-probe     path to probe-power.sh on this host
#   --thermal-probe   path to probe-thermals.sh on this host
#   --engine-helper   path to engines/llama-server.sh on this host
#
# Per-cell flow:
#   1) launch llama-server with --ctx ctx --parallel concurrency
#   2) wait /health
#   3) start power + thermal samplers
#   4) issue N prompts (matching this cell), record decode/prefill/TTFT
#   5) stop samplers, stop llama-server
#   6) write cell.json + samplers CSV; touch .done

set -euo pipefail

BACKEND="" MODEL="" GRID="" PROMPTS="" OUT=""
SAMPLER_POWER="" SAMPLER_THERMAL=""
POWER_PROBE="" THERMAL_PROBE="" ENGINE_HELPER=""

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
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

for v in BACKEND MODEL GRID PROMPTS OUT SAMPLER_POWER SAMPLER_THERMAL POWER_PROBE THERMAL_PROBE ENGINE_HELPER; do
    [[ -n "${!v}" ]] || { echo "missing --${v,,}" >&2; exit 2; }
done

mkdir -p "$OUT"
log() { printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"; }

CONTEXTS=( $(jq -r '.contexts[]'      "$GRID") )
GENS=(     $(jq -r '.gen_lengths[]'   "$GRID") )
CONCS=(    $(jq -r '.concurrencies[]' "$GRID") )
N_PER_CELL="$(jq -r '.n_per_cell' "$GRID")"
WARMUP="$(jq -r '.warmup_discard' "$GRID")"

PORT_BASE="${BENCH_PORT_BASE:-19000}"

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
        return 0
    fi

    log "=== cell ctx=$ctx gen=$gen conc=$conc ==="
    local port=$((PORT_BASE + RANDOM % 1000))
    # Wait until free
    while lsof -ti tcp:"$port" >/dev/null 2>&1; do port=$((port + 1)); done

    # 1) Launch llama-server
    local server_pid
    # ctx_total = ctx * conc to provide room for parallel sessions
    local ctx_total=$(( ctx * conc + 1024 ))
    server_pid="$(BENCH_LOG_DIR="$dir" "$ENGINE_HELPER" start "$BACKEND" "$MODEL" "$port" "$ctx_total" "$conc")"
    log "  llama-server pid=$server_pid port=$port ctx_total=$ctx_total"

    # 2) Wait for /health — Q8 27B/35B model load over mmap'd disk can take
    # 60-180s on cold cache; allow 10 min before giving up.
    if ! "$ENGINE_HELPER" wait-ready "$port" 600 >/dev/null; then
        log "  FAIL: server didn't become ready"
        "$ENGINE_HELPER" stop "$port" >/dev/null 2>&1 || true
        echo "server-timeout" > "$dir/.error"
        return 1
    fi

    # 3) Samplers (each runs until SIGTERM)
    "$POWER_PROBE"   "$dir/power.csv"   "$SAMPLER_POWER"   &  local pwr_pid=$!
    "$THERMAL_PROBE" "$dir/thermals.csv" "$SAMPLER_THERMAL" & local thm_pid=$!

    # 4) Issue prompts for THIS cell. The prompt corpus already has $N_PER_CELL
    # entries with matching context_target+gen_target; we filter for them.
    local results="$dir/inferences.jsonl"
    : > "$results"
    local idx=0
    jq -c --argjson ctx "$ctx" --argjson gen "$gen" \
        'select(.context_target == $ctx and .gen_target == $gen)' "$PROMPTS" \
        | while read -r row; do
            idx=$((idx+1))
            local prompt; prompt="$(jq -r '.prompt' <<<"$row")"
            local pid_label; pid_label="$(jq -r '.id' <<<"$row")"
            local t0 t1 ttft body usage decode_tps prefill_tps prompt_tok gen_tok
            t0="$(date +%s.%N)"
            # Use /completion which gives us timings in the response.
            body="$(curl -sS --max-time 600 -X POST "http://127.0.0.1:$port/completion" \
                -H 'Content-Type: application/json' \
                -d "$(jq -n --arg p "$prompt" --argjson n "$gen" \
                    '{prompt:$p, n_predict:$n, temperature:0, seed:42, cache_prompt:false, stream:false}')" 2>/dev/null)"
            t1="$(date +%s.%N)"
            if [[ -z "$body" ]]; then
                log "    inference $idx FAILED"
                continue
            fi
            decode_tps="$(jq -r '.timings.predicted_per_second // 0' <<<"$body")"
            prefill_tps="$(jq -r '.timings.prompt_per_second // 0' <<<"$body")"
            prompt_tok="$(jq -r '.timings.prompt_n // 0' <<<"$body")"
            gen_tok="$(jq -r '.timings.predicted_n // 0' <<<"$body")"
            ttft="$(jq -r '.timings.prompt_ms // 0' <<<"$body")"
            jq -nc --arg id "$pid_label" --argjson idx "$idx" \
                  --arg t0 "$t0" --arg t1 "$t1" \
                  --argjson decode "$decode_tps" --argjson prefill "$prefill_tps" \
                  --argjson ptok "$prompt_tok" --argjson gtok "$gen_tok" \
                  --argjson ttft_ms "$ttft" \
                  '{id:$id, idx:$idx, t0:($t0|tonumber), t1:($t1|tonumber),
                    decode_tps:$decode, prefill_tps:$prefill, prompt_tokens:$ptok,
                    gen_tokens:$gtok, ttft_ms:$ttft_ms}' >> "$results"
        done

    # 5) Stop samplers + server
    kill "$pwr_pid" "$thm_pid" 2>/dev/null || true
    wait "$pwr_pid" "$thm_pid" 2>/dev/null || true
    "$ENGINE_HELPER" stop "$port" || true

    # 6) Cell summary
    local summary; summary="$(jq -s --argjson w "$WARMUP" '
        sort_by(.idx)
        | .[$w:]
        | { n: length,
            decode_tps_mean:   (map(.decode_tps)   | add / length),
            decode_tps_median: (sort_by(.decode_tps)   | .[length/2|floor].decode_tps),
            prefill_tps_mean:  (map(.prefill_tps)  | add / length),
            ttft_ms_mean:      (map(.ttft_ms)      | add / length),
            prompt_tokens_max: (map(.prompt_tokens)| max),
            gen_tokens_total:  (map(.gen_tokens)   | add) }
    ' "$results")"
    jq -n --arg backend "$BACKEND" --arg model "$MODEL" \
          --argjson ctx "$ctx" --argjson gen "$gen" --argjson conc "$conc" \
          --arg started "$(date -u +%FT%TZ)" \
          --argjson summary "$summary" \
          '{backend:$backend, model:$model, ctx:$ctx, gen:$gen, conc:$conc,
            started:$started, summary:$summary}' > "$dir/cell.json"
    touch "$dir/.done"
    log "  cell done — decode_mean=$(jq -r '.summary.decode_tps_mean' <"$dir/cell.json")"
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
