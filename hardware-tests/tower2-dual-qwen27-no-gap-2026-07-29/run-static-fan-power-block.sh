#!/usr/bin/env bash
#
# Prospective Tower2 symmetric-power / fixed-fan block runner.
#
# Default action is a read-only readiness check. --dry-run prints the frozen
# block. Only --run delegates to the guarded dual-vLLM harness.

set -Eeuo pipefail

ACTION="check"
MODE=""
POWER_W=""
REPLICATE=""
ORDER=""
FAN_BUDGET=100
BASE_HARNESS="$(dirname "$0")/dual-vllm-qwen27-30m.sh"
OUT_ROOT="${HOME}/thermal-tests/static-fan-power-blocks"
BLOCK_LOCK="/tmp/tower2-static-fan-power-block.lock"

POLICIES=()

usage() {
  cat <<'EOF'
Usage:
  run-static-fan-power-block.sh --check
  run-static-fan-power-block.sh --dry-run --mode qualify|measure --power W --replicate N [options]
  run-static-fan-power-block.sh --run --mode qualify|measure --power W --replicate N [options]

Options:
  --mode MODE          qualify: three 120-second safety bumps
                       measure: three independent 15-minute cells
  --power W            Symmetric per-GPU power cap, 200 through 550 W
  --replicate N        Positive block replicate
  --fan-budget N       Matched total fan duty: 100, 120, or 140 (default: 100)
  --order CSV          Permutation of the selected fan-budget policies.
                       Defaults to the frozen three-block Latin order
  --base-harness PATH  Guarded dual-vLLM harness
  --out-root PATH      Block metadata/log root
  -h, --help

Policy sets:
  100: EQ50,B60T40,B40T60
  120: EQ60,B70T50,B50T70
  140: EQ70,B80T60,B60T80

For first-time qualification, explicitly use the conservative order
EQ50,B40T60,B60T40 so the lowest top-card airflow runs last.
EOF
}

while (($#)); do
  case "$1" in
    --check) ACTION="check"; shift ;;
    --dry-run) ACTION="dry-run"; shift ;;
    --run) ACTION="run"; shift ;;
    --mode) MODE="${2:?missing value for --mode}"; shift 2 ;;
    --power) POWER_W="${2:?missing value for --power}"; shift 2 ;;
    --replicate) REPLICATE="${2:?missing value for --replicate}"; shift 2 ;;
    --fan-budget) FAN_BUDGET="${2:?missing value for --fan-budget}"; shift 2 ;;
    --order) ORDER="${2:?missing value for --order}"; shift 2 ;;
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

[[ "$MODE" == "qualify" || "$MODE" == "measure" ]] || {
  echo "--mode must be qualify or measure" >&2
  exit 2
}
[[ "$POWER_W" =~ ^[0-9]+$ ]] && ((POWER_W >= 200 && POWER_W <= 550)) || {
  echo "--power must be an integer from 200 through 550 W" >&2
  exit 2
}
[[ "$REPLICATE" =~ ^[1-9][0-9]*$ ]] || {
  echo "--replicate must be a positive integer" >&2
  exit 2
}
case "$FAN_BUDGET" in
  100) POLICIES=(EQ50 B60T40 B40T60) ;;
  120) POLICIES=(EQ60 B70T50 B50T70) ;;
  140) POLICIES=(EQ70 B80T60 B60T80) ;;
  *) echo "--fan-budget must be 100, 120, or 140" >&2; exit 2 ;;
esac

if [[ -z "$ORDER" ]]; then
  case $(((REPLICATE - 1) % 3)) in
    0) ORDER="${POLICIES[0]},${POLICIES[1]},${POLICIES[2]}" ;;
    1) ORDER="${POLICIES[1]},${POLICIES[2]},${POLICIES[0]}" ;;
    2) ORDER="${POLICIES[2]},${POLICIES[0]},${POLICIES[1]}" ;;
  esac
fi
IFS=, read -r -a ORDERED_POLICIES <<<"$ORDER"
[[ "${#ORDERED_POLICIES[@]}" -eq 3 ]] || {
  echo "--order must contain exactly three comma-separated policies" >&2
  exit 2
}
sorted_order="$(printf '%s\n' "${ORDERED_POLICIES[@]}" | sort | paste -sd, -)"
expected_order="$(printf '%s\n' "${POLICIES[@]}" | sort | paste -sd, -)"
[[ "$sorted_order" == "$expected_order" ]] || {
  echo "--order must be a permutation of $(IFS=,; echo "${POLICIES[*]}")" >&2
  exit 2
}

policy_fans() {
  case "$1" in
    EQ50) printf '50 50\n' ;;
    B60T40) printf '60 40\n' ;;
    B40T60) printf '40 60\n' ;;
    EQ60) printf '60 60\n' ;;
    B70T50) printf '70 50\n' ;;
    B50T70) printf '50 70\n' ;;
    EQ70) printf '70 70\n' ;;
    B80T60) printf '80 60\n' ;;
    B60T80) printf '60 80\n' ;;
    *) echo "Unknown policy: $1" >&2; return 2 ;;
  esac
}

quote_command() {
  printf '%q ' "$@"
  printf '\n'
}

build_command() {
  local policy="$1"
  local bottom_fan top_fan duration cell_suffix tag_suffix min_power
  local -a command
  read -r bottom_fan top_fan < <(policy_fans "$policy")
  min_power=$(((POWER_W * 95 + 99) / 100))

  if [[ "$MODE" == "qualify" ]]; then
    duration=120
    cell_suffix="BUMP"
    tag_suffix="bump"
  else
    duration=900
    cell_suffix="15M"
    tag_suffix="15m"
  fi

  command=(
    "$BASE_HARNESS" --run
    --tag "ng-fan-${policy,,}-sym${POWER_W}-v3host-${tag_suffix}-r${REPLICATE}"
    --cell-id "NG-FAN-${policy}-SYM${POWER_W}-V3HOST-${cell_suffix}"
    --replicate "$REPLICATE"
    --duration "$duration"
    --warmup 120
    --cooldown 60
    --concurrency-gpu0 32
    --concurrency-gpu1 32
    --min-power-gpu0 "$min_power"
    --min-power-gpu1 "$min_power"
    --gpu0-power-limit "$POWER_W"
    --gpu1-power-limit "$POWER_W"
    --gpu0-fan-pct "$bottom_fan"
    --gpu1-fan-pct "$top_fan"
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
  )
  if [[ "$MODE" == "qualify" ]]; then
    command+=(--qualification-only --steady-state-protocol v1-slope)
  else
    command+=(--steady-state-protocol v2-fixed-quantized)
  fi
  printf '%s\0' "${command[@]}"
}

print_manifest() {
  local sequence=0 policy bottom_fan top_fan run_type
  [[ "$MODE" == "qualify" ]] && run_type="qualification" || run_type="model"
  printf 'block_replicate,sequence,mode,power_w,fan_budget_pct_points,policy,bottom_fan_pct,top_fan_pct,cell_id,run_type\n'
  for policy in "${ORDERED_POLICIES[@]}"; do
    sequence=$((sequence + 1))
    read -r bottom_fan top_fan < <(policy_fans "$policy")
    printf '%s,%s,%s,%s,%s,%s,%s,%s,NG-FAN-%s-SYM%s-V3HOST-%s,%s\n' \
      "$REPLICATE" "$sequence" "$MODE" "$POWER_W" "$FAN_BUDGET" "$policy" \
      "$bottom_fan" "$top_fan" "$policy" "$POWER_W" \
      "$([[ "$MODE" == "qualify" ]] && echo BUMP || echo 15M)" "$run_type"
  done
}

if [[ "$ACTION" == "dry-run" ]]; then
  print_manifest
  printf '\n'
  for policy in "${ORDERED_POLICIES[@]}"; do
    mapfile -d '' -t command < <(build_command "$policy")
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
  echo "Another static-fan power block is active: $BLOCK_LOCK" >&2
  exit 1
}

block_stamp="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
fan_suffix=""
[[ "$FAN_BUDGET" == 100 ]] || fan_suffix="-fan${FAN_BUDGET}"
block_dir="${OUT_ROOT}/${block_stamp}-sym${POWER_W}${fan_suffix}-${MODE}-r${REPLICATE}"
mkdir -p "$block_dir"
print_manifest >"$block_dir/block-manifest.csv"
printf 'ts_iso,sequence,policy,status,run_dir\n' >"$block_dir/block-results.csv"

sequence=0
for policy in "${ORDERED_POLICIES[@]}"; do
  sequence=$((sequence + 1))
  launch_log="$block_dir/step-${sequence}-${policy,,}.launch.log"
  printf '%s,%s,%s,started,\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$policy" \
    >>"$block_dir/block-results.csv"
  mapfile -d '' -t command < <(build_command "$policy")
  set +e
  "${command[@]}" 2>&1 | tee "$launch_log"
  status=${PIPESTATUS[0]}
  set -e
  run_dir="$(awk -F'Output: ' '/Output: /{print $2; exit}' "$launch_log")"
  if ((status != 0)); then
    printf '%s,%s,%s,failed,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$policy" "$run_dir" \
      >>"$block_dir/block-results.csv"
    echo "Block stopped: step ${sequence} policy ${policy} failed" >&2
    exit "$status"
  fi
  [[ -n "$run_dir" && -s "$run_dir/summary.json" ]] || {
    printf '%s,%s,%s,missing-summary,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$policy" "$run_dir" \
      >>"$block_dir/block-results.csv"
    echo "Block stopped: summary missing for ${policy}" >&2
    exit 1
  }
  if [[ "$MODE" == "qualify" ]]; then
    gate_file="$run_dir/qualification-result.json"
    gate_query='.passed == true'
  else
    gate_file="$run_dir/summary.json"
    gate_query='.quality_gates.internal_admissible_candidate == true'
  fi
  if ! jq -e "$gate_query" "$gate_file" >/dev/null; then
    printf '%s,%s,%s,inadmissible,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$policy" "$run_dir" \
      >>"$block_dir/block-results.csv"
    echo "Block stopped: ${policy} did not pass the ${MODE} gate" >&2
    exit 1
  fi
  printf '%s,%s,%s,pass,%s\n' "$(date -u +%FT%T.%3NZ)" "$sequence" "$policy" "$run_dir" \
    >>"$block_dir/block-results.csv"
done

(
  cd "$block_dir"
  sha256sum block-manifest.csv block-results.csv step-*.launch.log >SHA256SUMS
)
printf 'Block complete: %s\n' "$block_dir"
