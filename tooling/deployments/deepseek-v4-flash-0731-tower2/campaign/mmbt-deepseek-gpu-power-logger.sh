#!/usr/bin/env bash
# Five-second dual-GPU telemetry for both canonical and extended DeepSeek MMBT.
# Extended RUNNING status takes precedence; otherwise the canonical current
# cell is used. Appends to one continuous CSV so energy can be integrated by
# exact run name across the full campaign.
set -u

OUT="${1:-/tmp/bench-autopilot/deepseek-v4-flash-0731-gpu_power.csv}"
INT="${2:-5}"
mkdir -p "$(dirname "$OUT")"
if [ ! -f "$OUT" ]; then
  echo "ts,gpu,power_w,util_sm,util_mem,mem_used_mib,temp_c,sm_clk_mhz,cell" > "$OUT"
fi

while true; do
  ts=$(date -u +%FT%TZ)
  cell=$(python3 - <<'PY'
import json
from pathlib import Path

def read(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}

extended = read("/tmp/mmbt-deepseek-v4-flash-extended/status.json")
canonical = read("/tmp/bench-autopilot/status.json")
if extended.get("phase") == "RUNNING" and extended.get("run"):
    print(extended["run"])
else:
    current = canonical.get("current") or {}
    cell = current.get("cell") or ""
    if not cell:
        # During the supervisor's short `starting` phase the receipt already
        # exists but status.current has not been populated. Attribute only an
        # unfinished top-level canonical run; completed directories contain a
        # summary (or an explicit terminal-pathology label) and are excluded.
        logs = Path("/home/michael/bench-deepseek-v4-flash-0731/logs")
        unfinished = []
        for receipt in logs.glob("p[1-3]_*_deepseek-v4-flash-0731_v*/receipt.json"):
            run_dir = receipt.parent
            if not (run_dir / "summary.json").exists() and not (run_dir / "label.json").exists():
                unfinished.append(receipt)
        if unfinished:
            cell = max(unfinished, key=lambda path: path.stat().st_mtime).parent.name
    print(cell)
PY
)
  nvidia-smi \
    --query-gpu=index,power.draw,utilization.gpu,utilization.memory,memory.used,temperature.gpu,clocks.current.sm \
    --format=csv,noheader,nounits 2>/dev/null | while IFS=, read -r idx pw usm umem mem temp clk; do
      echo "${ts},$(echo "$idx" | tr -d ' '),$(echo "$pw" | tr -d ' '),$(echo "$usm" | tr -d ' '),$(echo "$umem" | tr -d ' '),$(echo "$mem" | tr -d ' '),$(echo "$temp" | tr -d ' '),$(echo "$clk" | tr -d ' '),${cell}" >> "$OUT"
    done
  sleep "$INT"
done
