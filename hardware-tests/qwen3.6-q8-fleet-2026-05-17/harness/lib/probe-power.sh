#!/usr/bin/env bash
# probe-power.sh — 1Hz power sampler that runs on each host and writes CSV
# until SIGTERM. Selects the right backend per host.
#
# Usage (run on the target host directly):
#   probe-power.sh <output_csv> <sampler>
# where <sampler> ∈ {nvidia-smi, rocm-smi, powermetrics}
#
# CSV columns: ts_wall_iso, ts_mono_s, device, power_w, util_pct, mem_used_mib
# Each row is one device sample. Multi-GPU hosts emit N rows per tick.

set -uo pipefail

OUT="${1:?usage: probe-power.sh <csv> <sampler>}"
SAMPLER="${2:?usage: probe-power.sh <csv> <sampler>}"

trap 'exit 0' TERM INT

mono() { awk 'BEGIN{getline x < "/proc/uptime"; split(x,a," "); print a[1]}'; }   # linux mono (uptime seconds)
# macOS fallback: ts since boot via sysctl
mono_macos() { echo "$(date +%s.%N) - $(sysctl -n kern.boottime | sed -n 's/.* sec = \([0-9]*\),.*/\1/p')" | bc -l; }

case "$SAMPLER" in
    nvidia-smi)
        echo "ts_wall_iso,ts_mono_s,device,power_w,util_pct,mem_used_mib" > "$OUT"
        while :; do
            wall="$(date -u +%FT%T.%3NZ)"
            tm="$(mono)"
            # one nvidia-smi call emits one row per GPU
            nvidia-smi --query-gpu=index,power.draw,utilization.gpu,memory.used \
                       --format=csv,noheader,nounits \
                | awk -v w="$wall" -v m="$tm" -F', ' '{printf "%s,%s,gpu%s,%s,%s,%s\n", w, m, $1, $2, $3, $4}' \
                >> "$OUT"
            sleep 1
        done
        ;;
    rocm-smi)
        echo "ts_wall_iso,ts_mono_s,device,power_w,util_pct,mem_used_mib" > "$OUT"
        while :; do
            wall="$(date -u +%FT%T.%3NZ)"
            tm="$(mono)"
            # rocm-smi outputs JSON; one entry per GPU. Strix Halo's iGPU is card0.
            rocm-smi --showpower --showuse --showmemuse --json 2>/dev/null \
                | python3 -c '
import sys, json
d=json.load(sys.stdin)
for k,v in d.items():
    if not k.startswith("card"): continue
    pw=v.get("Average Graphics Package Power (W)") or v.get("Current Socket Graphics Package Power (W)") or "0"
    util=v.get("GPU use (%)","0")
    mem=v.get("GPU Memory Allocated (VRAM%)","0")
    print(f"{k},{pw},{util},{mem}")
' | awk -v w="$wall" -v m="$tm" -F',' '{printf "%s,%s,%s,%s,%s,%s\n", w, m, $1, $2, $3, $4}' \
                >> "$OUT"
            sleep 1
        done
        ;;
    powermetrics)
        # macOS: powermetrics requires sudo AND doesn't expose die temperatures.
        # Use `macmon` instead (sudoless Rust tool reading IOReport framework).
        # Gives per-subsystem power and CPU/GPU die temps in Celsius.
        echo "ts_wall_iso,ts_mono_s,device,power_w,util_pct,mem_used_mib" > "$OUT"
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
    cpu_p = m.get("cpu_power", 0.0)
    gpu_p = m.get("gpu_power", 0.0)
    ane_p = m.get("ane_power", 0.0)
    ram_p = m.get("ram_power", 0.0)
    sys_p = m.get("sys_power", 0.0)
    cpu_u = m.get("cpu_usage_pct", 0.0) * 100
    gpu_u = (m.get("gpu_usage", [0,0])[1] if isinstance(m.get("gpu_usage"), list) else 0) * 100
    ram_used_mib = (m.get("memory", {}).get("ram_usage", 0) // 1024 // 1024)
    print(f"{wall},{mono:.3f},cpu,{cpu_p:.2f},{cpu_u:.1f},", flush=True)
    print(f"{wall},{mono:.3f},gpu,{gpu_p:.2f},{gpu_u:.1f},", flush=True)
    print(f"{wall},{mono:.3f},ane,{ane_p:.2f},,", flush=True)
    print(f"{wall},{mono:.3f},ram,{ram_p:.2f},,{ram_used_mib}", flush=True)
    print(f"{wall},{mono:.3f},sys,{sys_p:.2f},,", flush=True)
' >> "$OUT"
        ;;
    *)
        echo "unknown sampler: $SAMPLER" >&2
        exit 2
        ;;
esac
