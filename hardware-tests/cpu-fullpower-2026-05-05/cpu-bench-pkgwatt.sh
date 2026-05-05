#!/bin/bash
# CPU full-power bench: drives all 48 threads via stress-ng matrix and samples
# CPU package power from intel-rapl in parallel, alongside the standard
# thermlog.sh CPU/GPU thermal CSV.
#
# Why this exists: cpu-burn.sh logs Tctl/Tccd/MHz/GPU but NOT PkgWatt, which
# is the thing we actually need to know to verify "is the CPU pulling its
# full rated power?".
#
# Usage:
#   sudo -v   # prime cache; this script keeps it warm
#   ./cpu-bench-pkgwatt.sh [tag] [duration_s]
#
# Default: tag=cpu-pkgwatt, duration=300s
#
# Outputs (in ~/thermal-tests/):
#   run-YYYY-MM-DD-HHMM-<tag>.csv         — thermlog (CPU/GPU/NVMe temps)
#   run-YYYY-MM-DD-HHMM-<tag>-pkgwatt.csv — t_iso, energy_uj, watts (2s)
#   run-YYYY-MM-DD-HHMM-<tag>.log         — stdout from cpu-burn

set -u
TAG="${1:-cpu-pkgwatt}"
DURATION="${2:-300}"
DIR="$HOME/thermal-tests"
STAMP=$(date +%Y-%m-%d-%H%M)
PKG_CSV="$DIR/run-$STAMP-$TAG-pkgwatt.csv"

if ! sudo -n -v 2>/dev/null; then
  echo "FATAL: sudo cache empty. Run \`sudo -v\` first." >&2
  exit 1
fi

# Sudo keepalive in background — keeps the cache warm for the whole bench.
( while true; do sudo -n -v 2>/dev/null; sleep 60; done ) &
SUDO_KA=$!
trap 'kill $SUDO_KA 2>/dev/null; pkill -P $$ 2>/dev/null' EXIT INT TERM

# Sample energy_uj every ~2s and emit watts. Runs slightly longer than the
# bench so we capture cooldown for at least one sample past stress-ng exit.
PAD=10
SAMPLES=$(( (DURATION + PAD) / 2 ))

echo "Starting PkgWatt sampler ($SAMPLES samples, 2s each) -> $PKG_CSV"
sudo -n bash -c '
  echo "t_iso,energy_uj,watts"
  prev_e=$(cat /sys/class/powercap/intel-rapl:0/energy_uj)
  prev_t=$(date +%s.%N)
  for i in $(seq 1 '"$SAMPLES"'); do
    sleep 2
    cur_e=$(cat /sys/class/powercap/intel-rapl:0/energy_uj)
    cur_t=$(date +%s.%N)
    dt=$(echo "$cur_t - $prev_t" | bc -l)
    de=$((cur_e - prev_e))
    if [ "$de" -lt 0 ]; then
      max=$(cat /sys/class/powercap/intel-rapl:0/max_energy_range_uj)
      de=$((cur_e + max - prev_e))
    fi
    watts=$(echo "scale=2; $de / $dt / 1000000" | bc -l)
    echo "$(date -Iseconds),$cur_e,$watts"
    prev_e=$cur_e
    prev_t=$cur_t
  done
' > "$PKG_CSV" &
SAMPLER_PID=$!

sleep 1  # let sampler establish baseline

echo "=== Launching cpu-burn.sh tag=$TAG dur=${DURATION}s ==="
"$DIR/cpu-burn.sh" "$TAG" "$DURATION" 0

# Sampler should finish on its own (SAMPLES * 2s ≈ DURATION + PAD); wait briefly.
wait $SAMPLER_PID 2>/dev/null
echo "PkgWatt CSV: $PKG_CSV"

# Quick summary directly from CSV.
echo "=== PkgWatt summary ==="
awk -F, 'NR>1 && $3+0>0 {
  if(min==0||$3+0<min) min=$3+0
  if($3+0>max) max=$3+0
  sum+=$3; n++
}
END{
  if(n>0) printf "samples=%d  min=%.1fW  max=%.1fW  mean=%.1fW\n", n, min, max, sum/n
}' "$PKG_CSV"
