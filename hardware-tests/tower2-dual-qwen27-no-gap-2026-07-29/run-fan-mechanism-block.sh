#!/usr/bin/env bash
#
# Prospective Tower2 no-gap fan-mechanism block runner.
#
# The default action is a read-only readiness check. --dry-run prints the
# frozen three-cell block without touching GPU state. Only --run delegates to
# the guarded dual-vLLM harness.

set -Eeuo pipefail

ACTION="check"
FAMILY=""
LOADED_GPU=""
REPLICATE=""
ORDER=""
HEADROOM_WORKERS=""
BASE_HARNESS="$(dirname "$0")/dual-vllm-qwen27-30m.sh"
OUT_ROOT="${HOME}/thermal-tests/fan-isolation-blocks"
BLOCK_LOCK="/tmp/tower2-fan-isolation-block.lock"

usage() {
  cat <<'EOF'
Usage:
  run-fan-mechanism-block.sh --check
  run-fan-mechanism-block.sh --dry-run --family FAMILY --loaded-gpu 0|1 --replicate N [options]
  run-fan-mechanism-block.sh --run --family FAMILY --loaded-gpu 0|1 --replicate N [options]

Families:
  own-saturated    Loaded GPU fan steps 30/50/70%; idle neighbor fixed 50%
  neighbor-airflow
                   Loaded GPU fixed 50%; idle neighbor fan steps 30/50/70%
  headroom         Loaded GPU fan steps under a 350 W cap and bounded load;
                   requires --headroom-workers

Options:
  --order CSV              Permutation of 30,50,70. Default is the frozen
                           Latin-square order selected by replicate.
  --headroom-workers N     Calibrated loaded-GPU concurrency for headroom
  --base-harness PATH      Guarded dual-vLLM harness
  --out-root PATH          Block metadata/log root
  -h, --help

The first three default orders are:
  replicate 1: 30,50,70
  replicate 2: 50,70,30
  replicate 3: 70,30,50
EOF
}

while (($#)); do
  case "$1" in
    --check) ACTION="check"; shift ;;
    --dry-run) ACTION="dry-run"; shift ;;
    --run) ACTION="run"; shift ;;
    --family) FAMILY="${2:?missing value for --family}"; shift 2 ;;
    --loaded-gpu) LOADED_GPU="${2:?missing value for --loaded-gpu}"; shift 2 ;;
    --replicate) REPLICATE="${2:?missing value for --replicate}"; shift 2 ;;
    --order) ORDER="${2:?missing value for --order}"; shift 2 ;;
    --headroom-workers) HEADROOM_WORKERS="${2:?missing value for --headroom-workers}"; shift 2 ;;
    --base-harness) BASE_HARNESS="${2:?missing value for --base-harness}"; shift 2 ;;
    --out-root) OUT_ROOT="${2:?missing value for --out-root}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$ACTION" == "check" ]]; then
  [[ -x "$BASE_HARNESS" ]] || {
    echo "Base harness is not executable: $BASE_HARNESS" >&2
    exit 1
  }
  exec "$BASE_HARNESS" --check
fi

case "$FAMILY" in
  own-saturated|neighbor-airflow|headroom) ;;
  *) echo "--family must be own-saturated, neighbor-airflow, or headroom" >&2; exit 2 ;;
esac
[[ "$LOADED_GPU" == "0" || "$LOADED_GPU" == "1" ]] || {
  echo "--loaded-gpu must be 0 or 1" >&2
  exit 2
}
[[ "$REPLICATE" =~ ^[1-9][0-9]*$ ]] || {
  echo "--replicate must be a positive integer" >&2
  exit 2
}
if [[ "$FAMILY" == "headroom" ]]; then
  [[ "$HEADROOM_WORKERS" =~ ^[1-9][0-9]*$ ]] || {
    echo "headroom family requires positive --headroom-workers" >&2
    exit 2
  }
fi

if [[ -z "$ORDER" ]]; then
  case $(((REPLICATE - 1) % 3)) in
    0) ORDER="30,50,70" ;;
    1) ORDER="50,70,30" ;;
    2) ORDER="70,30,50" ;;
  esac
fi
IFS=, read -r -a STEPS <<<"$ORDER"
[[ "${#STEPS[@]}" -eq 3 ]] || {
  echo "--order must contain exactly three comma-separated steps" >&2
  exit 2
}
sorted_order="$(printf '%s\n' "${STEPS[@]}" | sort -n | paste -sd, -)"
[[ "$sorted_order" == "30,50,70" ]] || {
  echo "--order must be a permutation of 30,50,70" >&2
  exit 2
}

loaded_position="bottom"
((LOADED_GPU == 1)) && loaded_position="top"
family_code="OWN"
[[ "$FAMILY" == "neighbor-airflow" ]] && family_code="NEIGHBOR"
[[ "$FAMILY" == "headroom" ]] && family_code="HEADROOM"

quote_command() {
  printf '%q ' "$@"
  printf '\n'
}

build_command() {
  local step="$1"
  local loaded_workers=32
  local loaded_limit=300
  local loaded_min_power=285
  local gpu0_workers=0 gpu1_workers=0
  local gpu0_limit=300 gpu1_limit=300
  local gpu0_fan=50 gpu1_fan=50
  local gpu0_min_power=0 gpu1_min_power=0
  local tag cell_id
  local -a command

  if [[ "$FAMILY" == "headroom" ]]; then
    loaded_workers="$HEADROOM_WORKERS"
    loaded_limit=350
    loaded_min_power=270
  fi

  if ((LOADED_GPU == 0)); then
    gpu0_workers="$loaded_workers"
    gpu0_limit="$loaded_limit"
    gpu0_min_power="$loaded_min_power"
    if [[ "$FAMILY" == "neighbor-airflow" ]]; then
      gpu1_fan="$step"
    else
      gpu0_fan="$step"
    fi
  else
    gpu1_workers="$loaded_workers"
    gpu1_limit="$loaded_limit"
    gpu1_min_power="$loaded_min_power"
    if [[ "$FAMILY" == "neighbor-airflow" ]]; then
      gpu0_fan="$step"
    else
      gpu1_fan="$step"
    fi
  fi

  tag="ng-faniso-${FAMILY}-load${loaded_position}-f${step}-v3host-15m-r${REPLICATE}"
  cell_id="NG-FANISO-${family_code}-LOAD${loaded_position^^}-F${step}-V3HOST-15M"
  command=(
    "$BASE_HARNESS" --run
    --tag "$tag"
    --cell-id "$cell_id"
    --replicate "$REPLICATE"
    --duration 900
    --warmup 120
    --cooldown 60
    --concurrency-gpu0 "$gpu0_workers"
    --concurrency-gpu1 "$gpu1_workers"
    --min-power-gpu0 "$gpu0_min_power"
    --min-power-gpu1 "$gpu1_min_power"
    --gpu0-power-limit "$gpu0_limit"
    --gpu1-power-limit "$gpu1_limit"
    --gpu0-fan-pct "$gpu0_fan"
    --gpu1-fan-pct "$gpu1_fan"
    --gpu-abort-c 85
    --max-start-temp-gpu0 45
    --max-start-temp-gpu1 45
    --max-start-cpu-tctl 70
    --max-start-nvme 41.9
    --max-idle-power-gpu0 50
    --max-idle-power-gpu1 50
    --telemetry-ms 250
    --nvml-clock-base-ms 173
    --nvml-clock-jitter-ms 101
    --preflight-soak 300
    --preflight-timeout 3600
    --steady-state-protocol v2-fixed-quantized
  )
  if [[ "$FAMILY" == "headroom" ]]; then
    command+=(
      "--loaded-power-mode-gpu${LOADED_GPU}" headroom
      "--max-power-gpu${LOADED_GPU}" 300
      --headroom-max-cap-fraction 0
    )
  fi
  printf '%s\0' "${command[@]}"
}

print_manifest() {
  local sequence=0 step
  printf 'block_replicate,sequence,family,loaded_gpu,loaded_position,fan_step_pct,cell_id,run_type\n'
  for step in "${STEPS[@]}"; do
    sequence=$((sequence + 1))
    printf '%s,%s,%s,%s,%s,%s,NG-FANISO-%s-LOAD%s-F%s-V3HOST-15M,model\n' \
      "$REPLICATE" "$sequence" "$FAMILY" "$LOADED_GPU" "$loaded_position" "$step" \
      "$family_code" "${loaded_position^^}" "$step"
  done
}

if [[ "$ACTION" == "dry-run" ]]; then
  print_manifest
  printf '\n'
  for step in "${STEPS[@]}"; do
    mapfile -d '' -t command < <(build_command "$step")
    quote_command "${command[@]}"
  done
  exit 0
fi

[[ -x "$BASE_HARNESS" ]] || {
  echo "Base harness is not executable: $BASE_HARNESS" >&2
  exit 1
}
command -v jq >/dev/null || {
  echo "jq is required" >&2
  exit 1
}

exec 8>"$BLOCK_LOCK"
flock -n 8 || {
  echo "Another fan-isolation block is active: $BLOCK_LOCK" >&2
  exit 1
}

block_stamp="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
block_dir="${OUT_ROOT}/${block_stamp}-${FAMILY}-load${loaded_position}-r${REPLICATE}"
mkdir -p "$block_dir"
print_manifest > "$block_dir/block-manifest.csv"
printf 'ts_iso,sequence,fan_step_pct,status,run_dir\n' > "$block_dir/block-results.csv"

sequence=0
for step in "${STEPS[@]}"; do
  sequence=$((sequence + 1))
  launch_log="$block_dir/step-${sequence}-f${step}.launch.log"
  printf '%s,%s,%s,started,\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$step" \
    >> "$block_dir/block-results.csv"
  mapfile -d '' -t command < <(build_command "$step")
  set +e
  "${command[@]}" 2>&1 | tee "$launch_log"
  status=${PIPESTATUS[0]}
  set -e
  run_dir="$(awk -F'Output: ' '/Output: /{print $2; exit}' "$launch_log")"
  if ((status != 0)); then
    printf '%s,%s,%s,failed,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$step" "$run_dir" \
      >> "$block_dir/block-results.csv"
    echo "Block stopped: step ${sequence} fan ${step}% failed" >&2
    exit "$status"
  fi
  [[ -n "$run_dir" && -s "$run_dir/summary.json" ]] || {
    printf '%s,%s,%s,missing-summary,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$step" "$run_dir" \
      >> "$block_dir/block-results.csv"
    echo "Block stopped: completed step has no summary" >&2
    exit 1
  }
  jq -e '.quality_gates.internal_admissible_candidate == true' "$run_dir/summary.json" >/dev/null || {
    printf '%s,%s,%s,inadmissible,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$step" "$run_dir" \
      >> "$block_dir/block-results.csv"
    echo "Block stopped: step ${sequence} is not internally admissible" >&2
    exit 1
  }
  printf '%s,%s,%s,pass,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$step" "$run_dir" \
    >> "$block_dir/block-results.csv"
done

sha256sum "$block_dir"/block-*.csv "$block_dir"/*.launch.log > "$block_dir/SHA256SUMS"
printf '%s\n' "$block_dir"
