#!/usr/bin/env bash
# live-snapshot.sh — periodic in-flight aggregation + snapshot renderer.
# 1. Pulls Tower2's local /tmp cells into RUN_DIR (mirrors what the watcher
#    does for remote hosts).
# 2. Runs aggregate.sh.
# 3. Renders LIVE-SNAPSHOT.md with current headline numbers.
# 4. Commits the snapshot.
#
# Safe to run any time — operates on whatever cells have completed.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

RUN_DIR="${1:?usage: live-snapshot.sh <run_dir>}"
[[ -d "$RUN_DIR" ]] || die "no such dir: $RUN_DIR"

log "live-snapshot @ $RUN_DIR"

# 1. Sync Tower2 local /tmp → RUN_DIR (the watcher skips local hosts)
for tmpdir in /tmp/bench-fleet-out-tower2-*; do
    [[ -d "$tmpdir" ]] || continue
    base="$(basename "$tmpdir")"
    # Example: bench-fleet-out-tower2-qwen3.6-27b-cuda-762012
    # Tail off the PID + walk back to find model+backend
    # Simpler: parse from the name
    suffix="${base#bench-fleet-out-tower2-}"
    # Strip trailing -<pid>
    suffix="${suffix%-*}"
    # Now: qwen3.6-27b-cuda or qwen3.6-35b-a3b-cuda
    backend="${suffix##*-}"
    model="${suffix%-$backend}"
    dest="$RUN_DIR/tower2/$model/$backend"
    mkdir -p "$dest"
    rsync -a --exclude='llama-server-*.log' "$tmpdir/" "$dest/" >/dev/null 2>&1 || true
done

# 2. Aggregate
"$SCRIPT_DIR/aggregate.sh" "$RUN_DIR" >/dev/null 2>&1 || log "  aggregate had warnings"

# 3. Render LIVE-SNAPSHOT.md
SNAP="$RUN_DIR/LIVE-SNAPSHOT.md"
GEN_TIME="$(date -u +%FT%TZ)"
TOTAL_CELLS="$(jq 'length' "$RUN_DIR/aggregate/cells.jsonl" 2>/dev/null || echo 0)"
# Count cells actually committed (have .done)
TOTAL_DONE="$(find "$RUN_DIR" -name .done 2>/dev/null | wc -l)"

cat > "$SNAP" <<EOF
# Bench-fleet live snapshot

_Generated: $GEN_TIME — based on cells completed so far_

Run dir: \`$(basename "$RUN_DIR")\`

## Cells completed: **$TOTAL_DONE** of 288 target

\`\`\`
target: 4 hosts × 2 models × 36 cells = 288 cells
        (M5 27B backfill runs after orchestrator's M5 35B leg ends)
\`\`\`

## Headline — best (host × model × backend) cell observed so far

Power filtered to GPU silicon per host (gpu0-only on Blackwell 6000 Tower + DGX Spark, card0 on EVO X2, gpu on M5 Max MacBook Pro).
Wall-AC reported only on M5 Max (macmon \`sys\`). \`temp_c_max\` is labeled by the sensor it came from — note the EVO X2's Strix Halo APU exposes only edge.

| host | model | backend | cells | best agg tok/s | at cell | best per-slot tok/s | at cell | prefill | TTFT ms | silicon mean W | silicon max W | wall mean W | sensor | max °C | tok/s/W silicon | tok/s/W wall |
|------|-------|---------|------:|---------------:|---------|---------------------:|---------|--------:|--------:|---------------:|--------------:|------------:|--------|-------:|----------------:|-------------:|
EOF

jq -r '
    .[] |
    (if .host=="tower2" then "Blackwell 6000 Tower"
     elif .host=="strix-halo" then "EVO X2"
     elif .host=="spark" then "DGX Spark"
     elif .host=="m5-mbp" then "M5 Max MacBook Pro"
     else .host end) as $display |
    "| \($display) | \(.model) | \(.backend) | \(.cells_complete) " +
    "| \(.best_aggregate_decode_tps | if . then (.*100|floor/100) else "—" end) " +
    "| \(.at_cell_agg) " +
    "| \(.best_per_slot_decode_tps  | if . then (.*100|floor/100) else "—" end) " +
    "| \(.at_cell_slot) " +
    "| \(.best_prefill_tps          | if . then (.*10|floor/10) else "—" end) " +
    "| \(.ttft_ms_at_best           | if . then (.|floor) else "—" end) " +
    "| \(.power_w_silicon_mean_at_best_agg | if . then . else "—" end) " +
    "| \(.power_w_silicon_max_at_best_agg  | if . then . else "—" end) " +
    "| \(.power_w_wall_mean_at_best_agg    | if . then . else "—" end) " +
    "| \(.temp_sensor // "—") " +
    "| \(.temp_c_max_at_best_agg    | if . then . else "—" end) " +
    "| \(.tok_per_watt_silicon_at_best_agg | if . then (.*1000|floor/1000) else "—" end) " +
    "| \(.tok_per_watt_wall_at_best_agg    | if . then (.*1000|floor/1000) else "—" end) |"
' "$RUN_DIR/aggregate/headline.json" >> "$SNAP"

cat >> "$SNAP" <<EOF

## Per-(host, model, backend) cell coverage

\`\`\`
EOF
for h in tower2 strix-halo spark m5-mbp; do
    case "$h" in
        tower2)     disp="Blackwell 6000 Tower" ;;
        strix-halo) disp="EVO X2" ;;
        spark)      disp="DGX Spark" ;;
        m5-mbp)     disp="M5 Max MacBook Pro" ;;
        *)          disp="$h" ;;
    esac
    for m in qwen3.6-27b qwen3.6-35b-a3b; do
        for b in cuda vulkan cuda-aarch64 metal; do
            dir="$RUN_DIR/$h/$m/$b"
            [[ -d "$dir" ]] || continue
            n=$(find "$dir" -name .done 2>/dev/null | wc -l)
            printf "  %-22s %-20s %-15s %d/36 cells\n" "$disp" "$m" "$b" "$n" >> "$SNAP"
        done
    done
done
cat >> "$SNAP" <<EOF
\`\`\`

## Cross-host comparison: same cell coordinates

The point of this study is to compare hardware at IDENTICAL cells. Where cells have completed on multiple hosts, here's the head-to-head.

| cell | host/model/backend | per-slot tok/s | aggregate tok/s | prefill tok/s | TTFT ms | silicon W | tok/W silicon |
|------|---------------------|---------------:|----------------:|--------------:|--------:|---------:|--------------:|
EOF

# For each commonly-completed cell coordinate, emit per-host rows.
# cells.jsonl is JSONL — must slurp (-s) to get a single array.
jq -rs '
    sort_by(.ctx, .gen, .conc, .host, .model)
    | group_by([.ctx, .gen, .conc])
    | map(select(length >= 2)) as $shared      # cells run on 2+ hosts
    | $shared[] | (.[0] | "\(.ctx)/\(.gen)/\(.conc)") as $cell
                | (length | tostring) as $nhosts
                | .[] |
      (if .host=="tower2" then "Blackwell 6000 Tower"
       elif .host=="strix-halo" then "EVO X2"
       elif .host=="spark" then "DGX Spark"
       elif .host=="m5-mbp" then "M5 Max MacBook Pro"
       else .host end) as $display |
      "| ctx=\($cell|split("/")[0]) gen=\($cell|split("/")[1]) conc=\($cell|split("/")[2]) | \($display)/\(.model)/\(.backend) " +
      "| \((.per_slot_decode_tps_mean // null) | if . then (.*100|floor/100|tostring) else "—" end) " +
      "| \((.aggregate_decode_tps_mean // null) | if . then (.*100|floor/100|tostring) else "—" end) " +
      "| \((.per_slot_prefill_tps_mean // null) | if . then (.*10|floor/10|tostring) else "—" end) " +
      "| \((.ttft_ms_mean // null) | if . then (.|floor|tostring) else "—" end) " +
      "| \((.power_w_silicon_mean // null) | tostring) " +
      "| \((.tok_per_watt_silicon_aggregate // null) | if . then (.*1000|floor/1000|tostring) else "—" end) |"
' "$RUN_DIR/aggregate/cells.jsonl" 2>/dev/null | head -300 >> "$SNAP"

cat >> "$SNAP" <<EOF

---
_Auto-generated by \`lib/live-snapshot.sh\` every 30 min during the run. Final REFERENCE.md will be rendered after all cells complete._
EOF

# 4. Commit
git -C "$BENCH_FLEET_ROOT" add "$(realpath --relative-to="$BENCH_FLEET_ROOT" "$SNAP")" \
                              "$(realpath --relative-to="$BENCH_FLEET_ROOT" "$RUN_DIR/aggregate")/" 2>/dev/null || true
if ! git -C "$BENCH_FLEET_ROOT" diff --cached --quiet 2>/dev/null; then
    git -C "$BENCH_FLEET_ROOT" \
        -c user.name="bench-fleet" -c user.email="bench-fleet@local" \
        commit -q -m "live-snapshot @ $GEN_TIME — $TOTAL_DONE cells done" 2>/dev/null || true
fi

log "  wrote $SNAP ($TOTAL_DONE cells)"
