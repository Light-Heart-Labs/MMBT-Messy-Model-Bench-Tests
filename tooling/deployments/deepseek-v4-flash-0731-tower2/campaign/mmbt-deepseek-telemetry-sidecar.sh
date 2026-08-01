#!/usr/bin/env bash
set -u

analyzer=/home/michael/bench-deepseek-v4-flash-0731/tooling/deployments/deepseek-v4-flash-0731-tower2/campaign/analyze_dual_gpu_telemetry.py
csv=/tmp/bench-autopilot/deepseek-v4-flash-0731-gpu_power.csv
canonical=/home/michael/bench-deepseek-v4-flash-0731/logs
extended=/home/michael/bench-deepseek-v4-flash-extended/logs
report=/tmp/bench-autopilot/deepseek-v4-flash-0731-dual-gpu-report.json
log=/tmp/bench-autopilot/telemetry-sidecar.log

while true; do
  if [ -s "$csv" ] && [ -f "$analyzer" ]; then
    python3 "$analyzer" \
      --csv "$csv" \
      --logs-dir "$canonical" \
      --logs-dir "$extended" \
      --write-run-artifacts \
      --output "$report" >>"$log" 2>&1 || true
  fi

  if python3 - <<'PY'
import json
from pathlib import Path

def read(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}

micro = read("/tmp/bench-autopilot/status.json")
extended = read("/tmp/mmbt-deepseek-v4-flash-extended/status.json")
raise SystemExit(0 if (
    micro.get("phase") == "COMPLETE"
    and micro.get("grand_done") == micro.get("grand_total") == 36
    and extended.get("phase") == "COMPLETE"
    and extended.get("done") == extended.get("total") == 12
) else 1)
PY
  then
    printf '%s telemetry sidecar complete\n' "$(date -u +%FT%TZ)" >>"$log"
    exit 0
  fi

  sleep 60
done
