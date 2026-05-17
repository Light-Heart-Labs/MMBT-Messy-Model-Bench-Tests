#!/bin/bash
# CPU-only burn for silent-hang isolation. Pushes all 48 threads while logging
# thermals via thermlog.sh. GPUs are left idle so this stresses CPU/PCIe/RAM/
# power-delivery in isolation from GPU inference load.
#
# NOTE: AVX matrix load is NOT representative for thermal-design validation
# (real workloads run cooler). Purpose here is stability — does pure CPU stress
# trigger the silent lockup that GPU burns did not.
#
# Usage: ./cpu-burn.sh [tag] [duration_s] [workers]
#   tag: optional label for output file, e.g. "cpu-60min" or "cpu-half-60min"
#   duration_s: default 300
#   workers: number of stress-ng threads. 0 (default) = all online CPUs (48 here).
#            Use 24 for half-load (one worker per physical core; kernel spreads).
#
# Output: ~/thermal-tests/run-YYYY-MM-DD-HHMM-<tag>.csv and .log

set -u
TAG="${1:-cpu}"
DURATION="${2:-300}"
WORKERS="${3:-0}"
STAMP=$(date +%Y-%m-%d-%H%M)
DIR="$HOME/thermal-tests"
CSV="$DIR/run-$STAMP-$TAG.csv"
LOG="$DIR/run-$STAMP-$TAG.log"
mkdir -p "$DIR"

SNAPS="30"
for m in $(seq 60 60 "$DURATION"); do SNAPS="$SNAPS $m"; done

exec > >(tee "$LOG") 2>&1

cleanup() {
  echo "--- cleanup ---"
  [[ -n "${LOGGER_PID:-}" ]] && kill "$LOGGER_PID" 2>/dev/null
  [[ -n "${LOAD_PID:-}" ]] && kill "$LOAD_PID" 2>/dev/null
  pkill -f "stress-ng" 2>/dev/null
  pkill -f "openssl speed" 2>/dev/null
}
trap cleanup EXIT INT TERM

# Pick stressor
N_LABEL=$([[ "$WORKERS" -eq 0 ]] && echo "all $(nproc) threads" || echo "$WORKERS threads")
if command -v stress-ng >/dev/null 2>&1; then
  STRESSOR="stress-ng"
  echo "=== Stressor: stress-ng --matrix $WORKERS --matrix-method all  (AVX-heavy, $N_LABEL) ==="
elif command -v openssl >/dev/null 2>&1; then
  STRESSOR="openssl"
  OSSL_M=$([[ "$WORKERS" -eq 0 ]] && nproc || echo "$WORKERS")
  echo "=== Stressor: openssl speed -multi $OSSL_M -evp aes-256-gcm  (AES-NI fallback, $N_LABEL) ==="
else
  echo "FATAL: neither stress-ng nor openssl found"; exit 1
fi

echo "=== GPU baseline (should stay near idle through the run) ==="
nvidia-smi --query-gpu=index,temperature.gpu,power.draw,utilization.gpu --format=csv,noheader

echo "=== Starting logger -> $CSV ==="
echo "t,cpu_tctl,cpu_ccd_max,cpu_mhz,gpu0_temp,gpu0_power,gpu0_mhz,gpu0_fan,gpu0_util,gpu1_temp,gpu1_power,gpu1_mhz,gpu1_fan,gpu1_util,nvme0,nvme1,nvme2" > "$CSV"
"$DIR/thermlog.sh" >> "$CSV" &
LOGGER_PID=$!

START=$(date +%s); END=$((START+DURATION))
echo "=== LOAD START $(date +%H:%M:%S) (${DURATION}s, $STRESSOR) ==="

if [[ "$STRESSOR" == "stress-ng" ]]; then
  stress-ng --matrix "$WORKERS" --matrix-method all --metrics -t "${DURATION}s" >/dev/null 2>&1 &
else
  openssl speed -multi "$OSSL_M" -evp aes-256-gcm -seconds "$DURATION" >/dev/null 2>&1 &
fi
LOAD_PID=$!

for t in $SNAPS; do
  while [ $(($(date +%s) - START)) -lt $t ]; do sleep 1; done
  echo "--- t+${t}s $(date +%H:%M:%S) ---"
  sensors | grep -E "Tctl|Tccd[1-4]|^Composite" | head -7
  awk '/cpu MHz/{s+=$4; n++} END{printf "CPU avg: %.0f MHz across %d threads\n", (n?s/n:0), n}' /proc/cpuinfo
  nvidia-smi --query-gpu=index,temperature.gpu,power.draw --format=csv,noheader
done

echo "=== STOP LOAD $(date +%H:%M:%S) ==="
kill $LOAD_PID 2>/dev/null
pkill -f "stress-ng" 2>/dev/null
pkill -f "openssl speed" 2>/dev/null
for i in 1 2 3 4 5; do kill -0 $LOAD_PID 2>/dev/null || break; sleep 1; done
kill -9 $LOAD_PID 2>/dev/null

for t in 30 60; do
  sleep 30
  echo "--- cooldown+${t}s $(date +%H:%M:%S) ---"
  sensors | grep -E "Tctl|Tccd[1-4]|^Composite" | head -7
done

echo "=== PEAKS ==="
awk -F, 'NR>1{
  if($2+0>mc)mc=$2+0; if($3+0>md)md=$3+0
  if($4+0>mhz)mhz=$4+0
  if($5+0>g0t)g0t=$5+0; if($10+0>g1t)g1t=$10+0
  for(i=15;i<=17;i++) if($i+0>nv)nv=$i+0
}
END{
  printf "CPU     Tctl %.1f C   Tccd %.1f C   peak avg MHz %.0f\n", mc, md, mhz
  printf "GPU     g0 %.0f C   g1 %.0f C  (should stay near idle)\n", g0t, g1t
  printf "NVMe    %.1f C (hottest)\n", nv
}' "$CSV"

echo "=== DONE — CSV: $CSV  LOG: $LOG ==="
