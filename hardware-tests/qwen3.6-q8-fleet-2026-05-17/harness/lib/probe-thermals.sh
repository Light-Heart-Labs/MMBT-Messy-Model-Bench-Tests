#!/usr/bin/env bash
# probe-thermals.sh — 1Hz thermal sampler. Same shape as probe-power.sh.
#
# Usage: probe-thermals.sh <output_csv> <sampler>
# Samplers: nvidia-smi+sensors, rocm-smi+sensors, powermetrics
#
# CSV columns: ts_wall_iso, ts_mono_s, sensor, temp_c
# One row per sensor reading per tick.

set -uo pipefail

OUT="${1:?usage: probe-thermals.sh <csv> <sampler>}"
SAMPLER="${2:?usage: probe-thermals.sh <csv> <sampler>}"

trap 'exit 0' TERM INT

echo "ts_wall_iso,ts_mono_s,sensor,temp_c" > "$OUT"

case "$SAMPLER" in
    nvidia-smi+sensors)
        while :; do
            wall="$(date -u +%FT%T.%3NZ)"
            tm="$(awk 'BEGIN{getline x < "/proc/uptime"; split(x,a," "); print a[1]}')"
            nvidia-smi --query-gpu=index,temperature.gpu --format=csv,noheader,nounits \
                | awk -v w="$wall" -v m="$tm" -F', ' '{printf "%s,%s,gpu%s,%s\n", w, m, $1, $2}' \
                >> "$OUT"
            # sensors: pull CPU/Tctl + ambient where available
            if command -v sensors >/dev/null 2>&1; then
                sensors -u 2>/dev/null | awk -v w="$wall" -v m="$tm" '
                    /^[a-zA-Z].*-(virtual|isa|pci|acpi)/ {chip=$0; next}
                    /^  [a-zA-Z].*:$/ {sensor=$1; gsub(":","",sensor); next}
                    /^    temp[0-9]_input:/ {
                        printf "%s,%s,%s,%.1f\n", w, m, sensor, $2
                    }
                ' >> "$OUT"
            fi
            sleep 1
        done
        ;;
    rocm-smi+sensors)
        while :; do
            wall="$(date -u +%FT%T.%3NZ)"
            tm="$(awk 'BEGIN{getline x < "/proc/uptime"; split(x,a," "); print a[1]}')"
            rocm-smi --showtemp --json 2>/dev/null \
                | python3 -c '
import sys, json
d=json.load(sys.stdin)
for k,v in d.items():
    if not k.startswith("card"): continue
    for sk,sv in v.items():
        if sk.startswith("Temperature"):
            label=sk.replace("Temperature ","").replace("(Sensor)","").strip()
            print(f"{k}-{label},{sv}")
' | awk -v w="$wall" -v m="$tm" -F',' '{printf "%s,%s,%s,%s\n", w, m, $1, $2}' \
                >> "$OUT"
            if command -v sensors >/dev/null 2>&1; then
                sensors -u 2>/dev/null | awk -v w="$wall" -v m="$tm" '
                    /^  [a-zA-Z].*:$/ {sensor=$1; gsub(":","",sensor); next}
                    /^    temp[0-9]_input:/ {
                        printf "%s,%s,%s,%.1f\n", w, m, sensor, $2
                    }
                ' >> "$OUT"
            fi
            sleep 1
        done
        ;;
    powermetrics)
        # macOS: use macmon (sudoless) — Apple's powermetrics doesn't expose die temps.
        MACMON_BIN="${MACMON_BIN:-/opt/homebrew/bin/macmon}"
        "$MACMON_BIN" pipe -i 1000 \
            | python3 -u -c '
import sys, json, time, datetime
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try: m=json.loads(line)
    except: continue
    wall=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00","Z")
    mono=time.monotonic()
    t = m.get("temp", {})
    cpu_t = t.get("cpu_temp_avg")
    gpu_t = t.get("gpu_temp_avg")
    if cpu_t is not None:
        print(f"{wall},{mono:.3f},cpu_die_avg,{cpu_t:.1f}", flush=True)
    if gpu_t is not None:
        print(f"{wall},{mono:.3f},gpu_die_avg,{gpu_t:.1f}", flush=True)
' >> "$OUT"
        ;;
    *)
        echo "unknown sampler: $SAMPLER" >&2
        exit 2
        ;;
esac
