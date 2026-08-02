#!/usr/bin/env bash
# Take an immutable, newline-complete telemetry snapshot at a clean cohort boundary.
set -euo pipefail

CSV=/home/michael/gemma4-campaign-state/telemetry/gemma4-31b-q4-gpu.csv
SNAPSHOT_ROOT=/home/michael/gemma4-campaign-state/telemetry/snapshots
LOGGER=mmbt-gemma4-power-logger.service
SIDECAR=mmbt-gemma4-telemetry-sidecar.service

if [ "$#" -ne 1 ]; then
  echo "usage: $0 $SNAPSHOT_ROOT/<cohort>.csv" >&2
  exit 2
fi
destination=$1
case "$destination" in
  "$SNAPSHOT_ROOT"/*.csv) ;;
  *) echo "ERROR: snapshot destination must be an absolute CSV under $SNAPSHOT_ROOT" >&2; exit 2 ;;
esac
if [ -e "$destination" ] || [ -e "$destination.tmp" ]; then
  echo "ERROR: refusing to overwrite telemetry snapshot: $destination" >&2
  exit 2
fi
if pgrep -af 'bench_autopilot.py|run_microbench.sh|tooling/harness.py|run_gemma4_extended_suites.py' \
    | grep -v snapshot_gemma4_telemetry >/dev/null; then
  echo "ERROR: benchmark work is active; telemetry snapshot requires a clean boundary" >&2
  exit 2
fi
if [ ! -s "$CSV" ]; then
  echo "ERROR: live telemetry CSV is missing or empty: $CSV" >&2
  exit 2
fi

logger_was_active=0
sidecar_was_active=0
systemctl --user is-active --quiet "$LOGGER" && logger_was_active=1
systemctl --user is-active --quiet "$SIDECAR" && sidecar_was_active=1
restart_services() {
  [ "$logger_was_active" -eq 0 ] || systemctl --user start "$LOGGER"
  [ "$sidecar_was_active" -eq 0 ] || systemctl --user start "$SIDECAR"
}
trap restart_services EXIT

# Stop the writer before copying so the snapshot cannot end with a partial row.
systemctl --user stop "$SIDECAR" "$LOGGER"
mkdir -p "$SNAPSHOT_ROOT"
cp --reflink=auto --preserve=mode,timestamps "$CSV" "$destination.tmp"
python3 - "$destination.tmp" <<'PY'
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
raw = path.read_bytes()
if not raw.endswith(b"\n"):
    raise SystemExit("telemetry snapshot does not end at a complete line")
with path.open(newline="") as handle:
    rows = list(csv.reader(handle))
expected = [
    "ts", "gpu", "endpoint_port", "power_limit_w", "power_w", "util_sm",
    "util_mem", "mem_used_mib", "temp_c", "sm_clk_mhz", "cell",
    "harness_pid", "cpu_package_power_w",
]
if not rows or rows[0] != expected:
    raise SystemExit("telemetry snapshot header drift")
if len(rows) < 3:
    raise SystemExit("telemetry snapshot has no paired GPU samples")
PY
mv "$destination.tmp" "$destination"
sha256sum "$destination"

restart_services
trap - EXIT
printf '%s\n' TELEMETRY_SNAPSHOT_COMPLETE
