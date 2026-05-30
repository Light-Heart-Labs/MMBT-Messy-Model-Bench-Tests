#!/usr/bin/env bash
# Lightweight dual-GPU telemetry sampler for bench runs. Appends one CSV row per
# sample: ISO time, then per-GPU power/util/mem/temp/clocks. Default 5s cadence.
# Pairs with status.json's current-cell so power can be attributed to a workload.
OUT="${1:-/tmp/bench-autopilot/gpu_power.csv}"
INT="${2:-5}"
mkdir -p "$(dirname "$OUT")"
if [ ! -f "$OUT" ]; then
  echo "ts,gpu,power_w,util_sm,util_mem,mem_used_mib,temp_c,sm_clk_mhz,cell" > "$OUT"
fi
while true; do
  ts=$(date -u +%FT%TZ)
  cell=$(python3 -c "import json;print((json.load(open('/tmp/bench-autopilot/status.json')).get('current') or {}).get('cell') or '')" 2>/dev/null)
  nvidia-smi --query-gpu=index,power.draw,utilization.gpu,utilization.memory,memory.used,temperature.gpu,clocks.current.sm \
    --format=csv,noheader,nounits 2>/dev/null | while IFS=, read -r idx pw usm umem mem temp clk; do
      echo "${ts},$(echo $idx|tr -d ' '),$(echo $pw|tr -d ' '),$(echo $usm|tr -d ' '),$(echo $umem|tr -d ' '),$(echo $mem|tr -d ' '),$(echo $temp|tr -d ' '),$(echo $clk|tr -d ' '),${cell}" >> "$OUT"
  done
  sleep "$INT"
done
