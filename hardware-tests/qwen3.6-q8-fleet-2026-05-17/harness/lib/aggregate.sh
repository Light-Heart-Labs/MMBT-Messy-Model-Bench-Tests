#!/usr/bin/env bash
# aggregate.sh — gather per-host cell.json + samplers into a cross-host pivot.
# Safe to run on a partial run (cells still streaming in).
#
# Inputs (under $RUN_DIR):
#   <host>/<model>/<backend>/ctx<C>_gen<G>_conc<P>/cell.json
#   <host>/<model>/<backend>/ctx<C>_gen<G>_conc<P>/power.csv
#   <host>/<model>/<backend>/ctx<C>_gen<G>_conc<P>/thermals.csv
#
# Outputs:
#   $RUN_DIR/aggregate/cells.jsonl          one row per cell (compact, flattened)
#   $RUN_DIR/aggregate/headline.json        host × model × backend best-cell pivot
#   $RUN_DIR/aggregate/headline.csv         same pivot as CSV

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

RUN_DIR="${1:?usage: aggregate.sh <run_dir>}"
OUT="$RUN_DIR/aggregate"
mkdir -p "$OUT"

log "aggregating $RUN_DIR -> $OUT"

cells_jsonl="$OUT/cells.jsonl"
: > "$cells_jsonl"

# Per-backend filter map: which device rows of power.csv count as the GPU
# silicon being measured, which device rows count as wall-AC (if exposed),
# which thermals.csv rows are the GPU sensor, and the label for that sensor.
# These filters fix the prior bug where M5's macmon emitted 5 rows per tick
# (cpu/gpu/ane/ram/sys) and the aggregator averaged ALL of them together —
# producing meaningless cross-subsystem numbers.
#
# Spec format: "exact:<val>"  → device == val
#              "contains:<v>" → val substring of device
#              ""             → no filter (legacy behavior)
filters_for_backend() {
    case "$1" in
        cuda|cuda-aarch64)
            # nvidia-smi: only the bench GPU. Tower2 has 2× PRO 6000; gpu1
            # idles at ~17 W and would contaminate the mean if averaged in.
            PWR_FILT="exact:gpu0";   PWR_WALL_FILT=""
            THM_FILT="exact:gpu0";   SENSOR_LABEL="gpu_die" ;;
        vulkan)
            # rocm-smi: Strix Halo APU exposes "Average Graphics Package Power"
            # (graphics block of the APU, NOT whole SoC) and only the
            # "Sensor edge" temperature — no junction is exposed by the
            # AMD kernel driver on this part.
            PWR_FILT="exact:card0";  PWR_WALL_FILT=""
            THM_FILT="contains:edge"; SENSOR_LABEL="gpu_edge" ;;
        metal)
            # macmon emits one row per subsystem per tick. Silicon = the GPU
            # IP block. Wall = the macmon-reported `sys` power (closest thing
            # we get to a wall-AC reading without a hardware power meter).
            PWR_FILT="exact:gpu";    PWR_WALL_FILT="exact:sys"
            THM_FILT="exact:gpu_die_avg"; SENSOR_LABEL="gpu_die_avg" ;;
        *)
            PWR_FILT="";             PWR_WALL_FILT=""
            THM_FILT="";             SENSOR_LABEL="unknown" ;;
    esac
}

# Flatten cell.json files into one compact row per cell.
# Compute silicon power_w_mean/_max + wall power (M5 only) + temp_c_max from
# the per-cell CSVs, with proper per-backend device filtering.
n_cells=0
while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    rel="${f#"$RUN_DIR/"}"
    host="${rel%%/*}"; rest="${rel#*/}"
    model="${rest%%/*}"; rest="${rest#*/}"
    backend="${rest%%/*}"
    cell_dir="$(dirname "$f")"
    pwr_csv="$cell_dir/power.csv"
    thm_csv="$cell_dir/thermals.csv"

    filters_for_backend "$backend"

    started_iso="$(jq -r '.started // ""' "$f" 2>/dev/null)"
    batch_wall_mean="$(jq -r '.aggregate.batch_wall_s_mean // 0' "$f" 2>/dev/null)"
    n_batches="$(jq -r '.n_batches // 10' "$f" 2>/dev/null)"

    pwr_si_mean="null"; pwr_si_max="null"
    pwr_wall_mean="null"; pwr_wall_max="null"
    temp_max="null"

    if [[ -n "$started_iso" ]] && [[ -s "$pwr_csv" ]] && (( $(wc -l < "$pwr_csv") > 1 )); then
        read pwr_si_mean pwr_si_max < <(python3 - "$pwr_csv" "$started_iso" "$batch_wall_mean" "$n_batches" "$PWR_FILT" <<'PY'
import sys, datetime
csv, started_iso, wall_mean, n_batches, filt = sys.argv[1:6]
wall_mean = float(wall_mean or 0); n_batches = int(n_batches or 10)
def matches(dev, spec):
    if not spec: return True
    kind, _, val = spec.partition(":")
    if kind == "exact":    return dev == val
    if kind == "contains": return val in dev
    return False
try: start = datetime.datetime.fromisoformat(started_iso.replace("Z","+00:00")).timestamp() - 5
except: start = 0
end = start + wall_mean * n_batches + 30
vals = []
with open(csv) as f:
    next(f, None)
    for line in f:
        p = line.rstrip().split(",")
        if len(p) < 4 or not p[3]: continue
        if not matches(p[2], filt): continue
        try: v = float(p[3])
        except: continue
        try: t = datetime.datetime.fromisoformat(p[0].replace("Z","+00:00")).timestamp()
        except: continue
        if start and (t < start or t > end): continue
        vals.append(v)
if vals: print(f"{sum(vals)/len(vals):.2f} {max(vals):.2f}")
else: print("null null")
PY
        )
        if [[ -n "$PWR_WALL_FILT" ]]; then
            read pwr_wall_mean pwr_wall_max < <(python3 - "$pwr_csv" "$started_iso" "$batch_wall_mean" "$n_batches" "$PWR_WALL_FILT" <<'PY'
import sys, datetime
csv, started_iso, wall_mean, n_batches, filt = sys.argv[1:6]
wall_mean = float(wall_mean or 0); n_batches = int(n_batches or 10)
def matches(dev, spec):
    if not spec: return True
    kind, _, val = spec.partition(":")
    if kind == "exact":    return dev == val
    if kind == "contains": return val in dev
    return False
try: start = datetime.datetime.fromisoformat(started_iso.replace("Z","+00:00")).timestamp() - 5
except: start = 0
end = start + wall_mean * n_batches + 30
vals = []
with open(csv) as f:
    next(f, None)
    for line in f:
        p = line.rstrip().split(",")
        if len(p) < 4 or not p[3]: continue
        if not matches(p[2], filt): continue
        try: v = float(p[3])
        except: continue
        try: t = datetime.datetime.fromisoformat(p[0].replace("Z","+00:00")).timestamp()
        except: continue
        if start and (t < start or t > end): continue
        vals.append(v)
if vals: print(f"{sum(vals)/len(vals):.2f} {max(vals):.2f}")
else: print("null null")
PY
            )
        fi
    fi

    if [[ -n "$started_iso" ]] && [[ -s "$thm_csv" ]] && (( $(wc -l < "$thm_csv") > 1 )); then
        temp_max="$(python3 - "$thm_csv" "$started_iso" "$batch_wall_mean" "$n_batches" "$THM_FILT" <<'PY'
import sys, datetime
csv, started_iso, wall_mean, n_batches, filt = sys.argv[1:6]
wall_mean = float(wall_mean or 0); n_batches = int(n_batches or 10)
def matches(dev, spec):
    if not spec: return True
    kind, _, val = spec.partition(":")
    if kind == "exact":    return dev == val
    if kind == "contains": return val in dev
    return False
try: start = datetime.datetime.fromisoformat(started_iso.replace("Z","+00:00")).timestamp() - 5
except: start = 0
end = start + wall_mean * n_batches + 30
vals = []
with open(csv) as f:
    next(f, None)
    for line in f:
        p = line.rstrip().split(",")
        if len(p) < 4 or not p[3]: continue
        if not matches(p[2], filt): continue
        try: v = float(p[3])
        except: continue
        try: t = datetime.datetime.fromisoformat(p[0].replace("Z","+00:00")).timestamp()
        except: continue
        if start and (t < start or t > end): continue
        vals.append(v)
print(f"{max(vals):.1f}" if vals else "null")
PY
        )"
    fi

    # Compact (single-line) row; merge in host/model/backend + sampler stats.
    # power_w_silicon_* = GPU/package only, comparable across hosts.
    # power_w_wall_*    = wall-AC where the sampler exposes it (M5 only).
    # tok_per_watt_*    = decode-tps / power, two flavors (silicon vs wall).
    # temp_sensor       = labels what temp_c_max measured (gpu_die / gpu_edge /
    #                     gpu_die_avg), so readers don't conflate sensors.
    jq -c \
       --arg host "$host" --arg model "$model" --arg backend "$backend" \
       --arg sensor "$SENSOR_LABEL" \
       --argjson pwr_si_mean   "$pwr_si_mean" \
       --argjson pwr_si_max    "$pwr_si_max" \
       --argjson pwr_wall_mean "$pwr_wall_mean" \
       --argjson pwr_wall_max  "$pwr_wall_max" \
       --argjson temp_max      "$temp_max" \
       '{
          host: $host, model: $model, backend: $backend,
          ctx: .ctx, gen: .gen, conc: .conc,
          per_slot_decode_tps_mean:   .per_slot.decode_tps_mean,
          per_slot_decode_tps_median: .per_slot.decode_tps_median,
          per_slot_decode_tps_sd:     .per_slot.decode_tps_sd,
          per_slot_prefill_tps_mean:  .per_slot.prefill_tps_mean,
          ttft_ms_mean:               .per_slot.ttft_ms_mean,
          aggregate_decode_tps_mean:  .aggregate.aggregate_decode_tps_mean,
          batch_wall_s_mean:          .aggregate.batch_wall_s_mean,
          prompt_tokens_actual:       .per_slot.prompt_tokens_max,
          gen_tokens_actual_per_inf:
            (if .per_slot.n and .per_slot.n > 0
             then (.per_slot.gen_tokens_total / .per_slot.n) else null end),
          total_tps_per_slot_actual:
            (if .aggregate.batch_wall_s_mean and .aggregate.batch_wall_s_mean > 0
                and .per_slot.prompt_tokens_max and .per_slot.gen_tokens_total and .per_slot.n
             then ((.per_slot.prompt_tokens_max + (.per_slot.gen_tokens_total / .per_slot.n))
                   / .aggregate.batch_wall_s_mean) else null end),
          cold_start_decode_tps:      .cold_start.per_slot_decode_tps_mean,
          cold_start_wall_s:          .cold_start.wall_s,
          n_batches_body:             .aggregate.n_batches_body,
          power_w_silicon_mean: $pwr_si_mean,
          power_w_silicon_max:  $pwr_si_max,
          power_w_wall_mean:    $pwr_wall_mean,
          power_w_wall_max:     $pwr_wall_max,
          temp_sensor:          $sensor,
          temp_c_max:           $temp_max,
          tok_per_watt_silicon_per_slot:
            (if ($pwr_si_mean != null and $pwr_si_mean > 0 and .per_slot.decode_tps_mean != null)
             then (.per_slot.decode_tps_mean / $pwr_si_mean) else null end),
          tok_per_watt_silicon_aggregate:
            (if ($pwr_si_mean != null and $pwr_si_mean > 0 and .aggregate.aggregate_decode_tps_mean != null)
             then (.aggregate.aggregate_decode_tps_mean / $pwr_si_mean) else null end),
          tok_per_watt_wall_aggregate:
            (if ($pwr_wall_mean != null and $pwr_wall_mean > 0 and .aggregate.aggregate_decode_tps_mean != null)
             then (.aggregate.aggregate_decode_tps_mean / $pwr_wall_mean) else null end)
        }' "$f" >> "$cells_jsonl" 2>/dev/null && n_cells=$((n_cells+1))
done < <(find "$RUN_DIR" -mindepth 5 -name cell.json 2>/dev/null)

log "  flattened $n_cells cells"

# Headline pivot per (host, model, backend). PRIMARY metrics are the three
# orthogonal request-time numbers that any AI hardware buyer needs:
#   - peak prefill rate (how fast prompts get processed)
#   - peak decode rate (how fast generation streams, short ctx)
#   - decode rate at long ctx (where memory hierarchy matters most)
# Plus TTFT at long ctx, since that's a separate user-experienced metric.
# All conc=1 (Path A scope). Multi-user is engine-bound under llama.cpp and held.
jq -s '
    [.[] | select(.conc == 1 and .per_slot_decode_tps_mean != null)]
    | group_by([.host, .model, .backend])
    | map(
        ((sort_by(-.per_slot_prefill_tps_mean) | .[0]) as $best_prefill
       | (sort_by(-.per_slot_decode_tps_mean)  | .[0]) as $best_decode
       | (map(select(.ctx == 16384))[0] // null) as $long_ctx
       | { host: $best_decode.host,
           model: $best_decode.model,
           backend: $best_decode.backend,
           cells_complete_conc1: length,
           peak_prefill_tps:         $best_prefill.per_slot_prefill_tps_mean,
           at_cell_prefill:          "ctx=\($best_prefill.ctx) gen=\($best_prefill.gen) conc=\($best_prefill.conc)",
           peak_decode_tps:          $best_decode.per_slot_decode_tps_mean,
           peak_decode_tps_sd:       $best_decode.per_slot_decode_tps_sd,
           at_cell_decode:           "ctx=\($best_decode.ctx) gen=\($best_decode.gen) conc=\($best_decode.conc)",
           decode_tps_at_ctx16k:     (if $long_ctx then $long_ctx.per_slot_decode_tps_mean else null end),
           decode_tps_at_ctx16k_sd:  (if $long_ctx then $long_ctx.per_slot_decode_tps_sd else null end),
           cold_start_decode_tps_at_peak: $best_decode.cold_start_decode_tps,
           ttft_ms_at_ctx16k:        (if $long_ctx then $long_ctx.ttft_ms_mean else null end),
           power_w_silicon_at_peak_decode: $best_decode.power_w_silicon_mean,
           power_w_wall_at_peak_decode:    $best_decode.power_w_wall_mean,
           temp_sensor:              $best_decode.temp_sensor,
           temp_c_max_at_peak_decode: $best_decode.temp_c_max })
      )
    | sort_by(.host, .model, .backend)' "$cells_jsonl" > "$OUT/headline.json"

# CSV mirror
{
echo "host,model,backend,cells_conc1,peak_prefill_tps,at_cell_prefill,peak_decode_tps,at_cell_decode,decode_at_ctx16k,ttft_ms_ctx16k,pwr_silicon_at_peak_decode,pwr_wall_at_peak_decode,temp_sensor,temp_c_max"
jq -r '.[] | [.host,.model,.backend,.cells_complete_conc1,
              .peak_prefill_tps,.at_cell_prefill,
              .peak_decode_tps,.at_cell_decode,
              .decode_tps_at_ctx16k,.ttft_ms_at_ctx16k,
              .power_w_silicon_at_peak_decode,
              .power_w_wall_at_peak_decode,
              .temp_sensor,.temp_c_max_at_peak_decode] | @csv' "$OUT/headline.json"
} > "$OUT/headline.csv"

log "  wrote $OUT/headline.json"
log "  wrote $OUT/headline.csv"
log "  wrote $OUT/cells.jsonl ($n_cells rows)"
