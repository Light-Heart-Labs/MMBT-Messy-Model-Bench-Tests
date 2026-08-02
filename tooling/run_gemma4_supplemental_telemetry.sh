#!/usr/bin/env bash
# Produce telemetry-matched supplemental observations for the two canonical
# bug-fix runs that completed before the telemetry sidecar existed. These runs
# use a distinct label and never replace or enter the canonical quality cohort.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="gemma4-31b-q4-telemetry-supplement"
MODEL="Gemma-4-31B-it-QAT-Q4_0"
MANIFEST="$ROOT/tooling/deployments/gemma4-31b-q4-tower2/benchmark-serving-manifest.json"
RUNNER="$ROOT/tooling/scripts/run_microbench.sh"
EXPECTED=(
  "p1_bugfix_${LABEL}_v1"
  "p1_bugfix_${LABEL}_v2"
)

cd "$ROOT"
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: refusing supplemental telemetry from a dirty worktree" >&2
  exit 2
fi
if systemctl --user is-active --quiet mmbt-gemma4-canonical-n3-r3.service; then
  echo "ERROR: canonical N=3 service is still active" >&2
  exit 2
fi
if pgrep -af 'bench_autopilot.py|run_microbench.sh|tooling/harness.py' | grep -v run_gemma4_supplemental_telemetry >/dev/null; then
  echo "ERROR: another benchmark harness is active" >&2
  exit 2
fi
for port in 8000 8001; do
  observed="$(curl -fsS "http://127.0.0.1:${port}/v1/models" | jq -r '.data[0].id')"
  if [ "$observed" != "$MODEL" ]; then
    echo "ERROR: port $port serves $observed, expected $MODEL" >&2
    exit 2
  fi
  if ! curl -fsS "http://127.0.0.1:${port}/slots" \
      | jq -e 'all(.[]; .is_processing == false)' >/dev/null; then
    echo "ERROR: port $port has an active request; retry at an idle boundary" >&2
    exit 2
  fi
done
mapfile -t limits < <(nvidia-smi --query-gpu=power.limit --format=csv,noheader,nounits)
if [ "${limits[*]}" != "500.00 500.00" ]; then
  echo "ERROR: GPU power limits are not both 500 W: ${limits[*]}" >&2
  exit 2
fi

for run in "${EXPECTED[@]}"; do
  if [ -e "logs/$run" ]; then
    echo "ERROR: supplemental run already exists and will not be overwritten: $run" >&2
    exit 2
  fi
done

common_env=(
  BENCH_LANE_COUNT=24
  BENCH_TEMP=1.0
  BENCH_TOP_P=0.95
  BENCH_TOP_K=64
  BENCH_MAX_OUTPUT_TOKENS_CAP=262144
  BENCH_SERVING_MANIFEST="$MANIFEST"
)

# N=2 has 24 total ordinals. Lane-count 24 assigns ordinal 0 (bugfix v1)
# exclusively to index 0 and ordinal 1 (bugfix v2) exclusively to index 1.
env "${common_env[@]}" BENCH_LANE_INDEX=0 \
  bash "$RUNNER" "$MODEL" 8000 "$LABEL" 2 "" "" 262144 &
pid0=$!
env "${common_env[@]}" BENCH_LANE_INDEX=1 \
  bash "$RUNNER" "$MODEL" 8001 "$LABEL" 2 "" "" 262144 &
pid1=$!

rc=0
wait "$pid0" || rc=1
wait "$pid1" || rc=1
if [ "$rc" -ne 0 ]; then
  echo "ERROR: a supplemental lane failed; preserve and audit both attempts" >&2
  exit 1
fi

for run in "${EXPECTED[@]}"; do
  for required in receipt.json transcript.jsonl summary.json workspace_final.tar.gz; do
    if [ ! -s "logs/$run/$required" ]; then
      echo "ERROR: $run missing $required" >&2
      exit 1
    fi
  done
  python3 tooling/scripts/extract_cost.py "logs/$run"
done

# The telemetry sidecar attributes and clips completed runs once per minute.
for _ in $(seq 1 36); do
  ready=1
  for run in "${EXPECTED[@]}"; do
    [ -s "logs/$run/cost.json" ] && [ -s "logs/$run/gpu_telemetry.json" ] || ready=0
  done
  [ "$ready" -eq 1 ] && break
  sleep 5
done
for run in "${EXPECTED[@]}"; do
  if [ ! -s "logs/$run/gpu_telemetry.json" ]; then
    echo "ERROR: telemetry sidecar did not materialize $run/gpu_telemetry.json" >&2
    exit 1
  fi
done

printf '%s\n' \
  "SUPPLEMENTAL_TELEMETRY_COMPLETE" \
  "canonical outcomes preserved: p1_bugfix_gemma4-31b-q4_v1/v2" \
  "supplements: ${EXPECTED[*]}"
