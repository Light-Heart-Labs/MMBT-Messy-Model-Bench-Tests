#!/usr/bin/env bash
#
# Guarded 30-minute dual-GPU saturation test for Tower2.
#
# GPU1: reuse the existing sanctuary-llm Qwen3.6-27B AWQ-INT4 vLLM server.
# GPU0: temporarily stop conflicting ODS GPU containers and launch an
#       identical vLLM image/model pinned to GPU 0.
#
# The default action is a non-invasive readiness check. Nothing is stopped
# and no load is generated unless --run is supplied.

set -Eeuo pipefail

ACTION="check"
TAG="qwen27-dual-600w-30m"
CELL_ID=""
REPLICATE=1
DURATION_S=1800
WARMUP_S=120
COOLDOWN_S=60
CONCURRENCY=32
CONCURRENCY_GPU0=""
CONCURRENCY_GPU1=""
MAX_TOKENS=1024
MIN_WARMUP_POWER_W=570
MIN_WARMUP_POWER_GPU0_W=""
MIN_WARMUP_POWER_GPU1_W=""
GPU0_POWER_LIMIT_W=600
GPU1_POWER_LIMIT_W=600
GPU_ABORT_C=92
MAX_START_TEMP_GPU0_C=45
MAX_START_TEMP_GPU1_C=45
MAX_IDLE_POWER_GPU0_W=50
MAX_IDLE_POWER_GPU1_W=50
TELEMETRY_INTERVAL_MS=1000
NVML_CLOCK_BASE_MS=173
NVML_CLOCK_JITTER_MS=101
AMBIENT_C=""
GPU0_PORT=8001
GPU1_PORT=8002
GPU0_CONTAINER="tower2-qwen27-gpu0-thermal"
SANCTUARY_CONTAINER="sanctuary-llm"
MODEL_PATH="/models/cyankiwi-Qwen3.6-27B-AWQ-INT4"
MODEL_SOURCE="/mnt/bulk/models"
OUT_ROOT="${HOME}/thermal-tests/runs"
LOCK_FILE="/tmp/dream-fleet-heavy.lock"
CONFLICTING_CONTAINERS=(
  ods-llama-server
  ods-whisper
  ods-comfyui
  ods-embeddings
)
CONFLICTING_USER_SERVICES=(
  openclaw-gateway.service
)

usage() {
  cat <<'EOF'
Usage:
  dual-vllm-qwen27-30m.sh [--check]
  dual-vllm-qwen27-30m.sh --run [options]

Options:
  --check                  Readiness checks only (default; no changes)
  --run                    Run the guarded saturation test
  --tag NAME               Output tag
  --cell-id NAME           Stable matrix-cell identifier (default: --tag)
  --replicate N            Positive replicate number (default: 1)
  --duration SECONDS       Measured duration (default: 1800)
  --warmup SECONDS         Saturation warm-up (default: 120)
  --cooldown SECONDS       Logged cooldown (default: 60)
  --concurrency N          Concurrent requests per GPU (default: 32)
  --concurrency-gpu0 N     GPU0 request workers; 0 leaves GPU0 idle
  --concurrency-gpu1 N     GPU1 request workers; 0 leaves GPU1 idle
  --max-tokens N           Maximum generated tokens/request (default: 1024)
  --min-power W            Required warm-up mean per GPU (default: 570)
  --min-power-gpu0 W       Required GPU0 warm-up mean (overrides --min-power)
  --min-power-gpu1 W       Required GPU1 warm-up mean (overrides --min-power)
  --gpu0-power-limit W     GPU0/bottom power limit (default: 600)
  --gpu1-power-limit W     GPU1/top power limit (default: 600)
  --gpu-abort-c C          Emergency GPU-temperature cutoff (default: 92)
  --max-start-temp-gpu0 C Maximum allowed GPU0 pre-run temperature (default: 45)
  --max-start-temp-gpu1 C Maximum allowed GPU1 pre-run temperature (default: 45)
  --max-idle-power-gpu0 W Abort if idle GPU0 exceeds this power (default: 50)
  --max-idle-power-gpu1 W Abort if idle GPU1 exceeds this power (default: 50)
  --telemetry-ms MS        GPU telemetry interval in milliseconds (default: 1000)
  --nvml-clock-base-ms MS  Independent NVML clock sampler base delay (default: 173)
  --nvml-clock-jitter-ms MS Random delay added to the NVML sampler (default: 101)
  --ambient-c C            Manually measured room/chassis inlet temperature

Before --run:
  sudo -v

Outputs:
  ~/thermal-tests/runs/<timestamp>-<tag>/
EOF
}

while (($#)); do
  case "$1" in
    --check) ACTION="check"; shift ;;
    --run) ACTION="run"; shift ;;
    --tag) TAG="${2:?missing value for --tag}"; shift 2 ;;
    --cell-id) CELL_ID="${2:?missing value for --cell-id}"; shift 2 ;;
    --replicate) REPLICATE="${2:?missing value for --replicate}"; shift 2 ;;
    --duration) DURATION_S="${2:?missing value for --duration}"; shift 2 ;;
    --warmup) WARMUP_S="${2:?missing value for --warmup}"; shift 2 ;;
    --cooldown) COOLDOWN_S="${2:?missing value for --cooldown}"; shift 2 ;;
    --concurrency) CONCURRENCY="${2:?missing value for --concurrency}"; shift 2 ;;
    --concurrency-gpu0) CONCURRENCY_GPU0="${2:?missing value for --concurrency-gpu0}"; shift 2 ;;
    --concurrency-gpu1) CONCURRENCY_GPU1="${2:?missing value for --concurrency-gpu1}"; shift 2 ;;
    --max-tokens) MAX_TOKENS="${2:?missing value for --max-tokens}"; shift 2 ;;
    --min-power) MIN_WARMUP_POWER_W="${2:?missing value for --min-power}"; shift 2 ;;
    --min-power-gpu0) MIN_WARMUP_POWER_GPU0_W="${2:?missing value for --min-power-gpu0}"; shift 2 ;;
    --min-power-gpu1) MIN_WARMUP_POWER_GPU1_W="${2:?missing value for --min-power-gpu1}"; shift 2 ;;
    --gpu0-power-limit) GPU0_POWER_LIMIT_W="${2:?missing value for --gpu0-power-limit}"; shift 2 ;;
    --gpu1-power-limit) GPU1_POWER_LIMIT_W="${2:?missing value for --gpu1-power-limit}"; shift 2 ;;
    --gpu-abort-c) GPU_ABORT_C="${2:?missing value for --gpu-abort-c}"; shift 2 ;;
    --max-start-temp-gpu0) MAX_START_TEMP_GPU0_C="${2:?missing value for --max-start-temp-gpu0}"; shift 2 ;;
    --max-start-temp-gpu1) MAX_START_TEMP_GPU1_C="${2:?missing value for --max-start-temp-gpu1}"; shift 2 ;;
    --max-idle-power-gpu0) MAX_IDLE_POWER_GPU0_W="${2:?missing value for --max-idle-power-gpu0}"; shift 2 ;;
    --max-idle-power-gpu1) MAX_IDLE_POWER_GPU1_W="${2:?missing value for --max-idle-power-gpu1}"; shift 2 ;;
    --telemetry-ms) TELEMETRY_INTERVAL_MS="${2:?missing value for --telemetry-ms}"; shift 2 ;;
    --nvml-clock-base-ms) NVML_CLOCK_BASE_MS="${2:?missing value for --nvml-clock-base-ms}"; shift 2 ;;
    --nvml-clock-jitter-ms) NVML_CLOCK_JITTER_MS="${2:?missing value for --nvml-clock-jitter-ms}"; shift 2 ;;
    --ambient-c) AMBIENT_C="${2:?missing value for --ambient-c}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for value in DURATION_S WARMUP_S COOLDOWN_S CONCURRENCY MAX_TOKENS TELEMETRY_INTERVAL_MS NVML_CLOCK_BASE_MS REPLICATE; do
  [[ "${!value}" =~ ^[1-9][0-9]*$ ]] || {
    echo "$value must be a positive integer" >&2
    exit 2
  }
done
CONCURRENCY_GPU0="${CONCURRENCY_GPU0:-$CONCURRENCY}"
CONCURRENCY_GPU1="${CONCURRENCY_GPU1:-$CONCURRENCY}"
for value in CONCURRENCY_GPU0 CONCURRENCY_GPU1; do
  [[ "${!value}" =~ ^[0-9]+$ ]] || {
    echo "$value must be a non-negative integer" >&2
    exit 2
  }
done
((CONCURRENCY_GPU0 + CONCURRENCY_GPU1 > 0)) || {
  echo "At least one GPU must have non-zero concurrency" >&2
  exit 2
}
((TELEMETRY_INTERVAL_MS >= 100)) || {
  echo "TELEMETRY_INTERVAL_MS must be at least 100" >&2
  exit 2
}
[[ "$NVML_CLOCK_JITTER_MS" =~ ^[0-9]+$ ]] || {
  echo "NVML_CLOCK_JITTER_MS must be a non-negative integer" >&2
  exit 2
}
((NVML_CLOCK_BASE_MS >= 20)) || {
  echo "NVML_CLOCK_BASE_MS must be at least 20" >&2
  exit 2
}
[[ "$MIN_WARMUP_POWER_W" =~ ^[0-9]+([.][0-9]+)?$ ]] || {
  echo "MIN_WARMUP_POWER_W must be numeric" >&2
  exit 2
}
if [[ -z "$MIN_WARMUP_POWER_GPU0_W" ]]; then
  ((CONCURRENCY_GPU0 == 0)) && MIN_WARMUP_POWER_GPU0_W=0 || MIN_WARMUP_POWER_GPU0_W="$MIN_WARMUP_POWER_W"
fi
if [[ -z "$MIN_WARMUP_POWER_GPU1_W" ]]; then
  ((CONCURRENCY_GPU1 == 0)) && MIN_WARMUP_POWER_GPU1_W=0 || MIN_WARMUP_POWER_GPU1_W="$MIN_WARMUP_POWER_W"
fi
for value in MIN_WARMUP_POWER_GPU0_W MIN_WARMUP_POWER_GPU1_W GPU0_POWER_LIMIT_W GPU1_POWER_LIMIT_W MAX_IDLE_POWER_GPU0_W MAX_IDLE_POWER_GPU1_W; do
  [[ "${!value}" =~ ^[0-9]+([.][0-9]+)?$ ]] || {
    echo "$value must be numeric" >&2
    exit 2
  }
done
for value in GPU_ABORT_C MAX_START_TEMP_GPU0_C MAX_START_TEMP_GPU1_C; do
  [[ "${!value}" =~ ^[0-9]+([.][0-9]+)?$ ]] || {
    echo "$value must be numeric" >&2
    exit 2
  }
done
if [[ -n "$AMBIENT_C" && ! "$AMBIENT_C" =~ ^-?[0-9]+([.][0-9]+)?$ ]]; then
  echo "AMBIENT_C must be numeric" >&2
  exit 2
fi
[[ "$TAG" =~ ^[A-Za-z0-9._-]+$ ]] || {
  echo "TAG may contain only letters, digits, dot, underscore, and dash" >&2
  exit 2
}
CELL_ID="${CELL_ID:-$TAG}"
[[ "$CELL_ID" =~ ^[A-Za-z0-9._-]+$ ]] || {
  echo "CELL_ID may contain only letters, digits, dot, underscore, and dash" >&2
  exit 2
}

log() {
  printf '[%s] %s\n' "$(date -u +%FT%TZ)" "$*"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    return 1
  }
}

sanctuary_model_ok() {
  docker inspect "$SANCTUARY_CONTAINER" \
    --format '{{json .Config.Cmd}}' 2>/dev/null \
    | grep -Fq "$MODEL_PATH" &&
  docker inspect "$SANCTUARY_CONTAINER" \
    --format '{{json .HostConfig.DeviceRequests}}' 2>/dev/null \
    | grep -Eq '"DeviceIDs":\["?1"?\]' &&
  curl -fsS -m 5 "http://127.0.0.1:${GPU1_PORT}/v1/models" \
    | jq -e '.data | length > 0' >/dev/null
}

sanctuary_idle_ok() {
  local metrics running waiting
  metrics="$(curl -fsS -m 5 "http://127.0.0.1:${GPU1_PORT}/metrics")" || return 1
  running="$(awk '$1 ~ /^vllm:num_requests_running[{]/ {sum+=$2} END{print sum+0}' <<<"$metrics")"
  waiting="$(awk '$1 ~ /^vllm:num_requests_waiting[{]/ {sum+=$2} END{print sum+0}' <<<"$metrics")"
  awk -v running="$running" -v waiting="$waiting" 'BEGIN{exit !((running+0)==0 && (waiting+0)==0)}'
}

sanctuary_test_load_isolated() {
  local metrics running waiting
  metrics="$(curl -fsS -m 5 "http://127.0.0.1:${GPU1_PORT}/metrics")" || return 1
  running="$(awk '$1 ~ /^vllm:num_requests_running[{]/ {sum+=$2} END{print sum+0}' <<<"$metrics")"
  waiting="$(awk '$1 ~ /^vllm:num_requests_waiting[{]/ {sum+=$2} END{print sum+0}' <<<"$metrics")"
  awk -v running="$running" -v waiting="$waiting" -v expected="$CONCURRENCY_GPU1" \
    'BEGIN{exit !((running+0)+(waiting+0)<=expected)}'
}

telemetry_probe() {
  nvidia-smi \
    --query-gpu=index,timestamp,temperature.gpu,temperature.memory,power.draw.average,power.draw.instant,power.limit,enforced.power.limit,clocks.current.graphics,clocks.current.sm,clocks.current.memory,utilization.gpu,utilization.memory,fan.speed,pstate,memory.used,clocks_event_reasons.sw_power_cap,clocks_event_reasons.hw_thermal_slowdown,clocks_event_reasons.hw_power_brake_slowdown,clocks_event_reasons.sw_thermal_slowdown,temperature.gpu.tlimit,clocks_event_reasons_counters.sw_power_cap,clocks_event_reasons_counters.sw_thermal_slowdown,clocks_event_reasons_counters.hw_thermal_slowdown,clocks_event_reasons_counters.hw_power_brake_slowdown \
    --format=csv,noheader,nounits
}

run_checks() {
  local failed=0
  log "Tower2 dual-Qwen27 readiness check"

  [[ "$(hostname)" == "Tower2" ]] || {
    echo "Wrong host: expected Tower2, got $(hostname)" >&2
    failed=1
  }

  for cmd in docker nvidia-smi curl jq awk flock lsof sensors python3; do
    require_command "$cmd" || failed=1
  done

  [[ -d "${MODEL_SOURCE}/cyankiwi-Qwen3.6-27B-AWQ-INT4" ]] || {
    echo "Missing model directory: ${MODEL_SOURCE}/cyankiwi-Qwen3.6-27B-AWQ-INT4" >&2
    failed=1
  }

  [[ "$(docker inspect "$SANCTUARY_CONTAINER" --format '{{.State.Running}}' 2>/dev/null || true)" == "true" ]] || {
    echo "$SANCTUARY_CONTAINER is not running" >&2
    failed=1
  }

  sanctuary_model_ok || {
    echo "GPU1 Sanctuary is not a healthy Qwen3.6-27B instance pinned to GPU 1" >&2
    failed=1
  }
  sanctuary_idle_ok || {
    echo "GPU1 Sanctuary has running or waiting production requests" >&2
    failed=1
  }

  telemetry_probe >/dev/null || {
    echo "Required NVIDIA telemetry fields are unavailable" >&2
    failed=1
  }

  local start_temp0 start_temp1
  read -r start_temp0 start_temp1 < <(
    nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits \
      | awk 'NR==1{a=$1} NR==2{b=$1} END{print a+0,b+0}'
  )
  awk -v value="$start_temp0" -v limit="$MAX_START_TEMP_GPU0_C" 'BEGIN{exit !(value>limit)}' && {
    echo "GPU0 start temperature ${start_temp0} C exceeds ${MAX_START_TEMP_GPU0_C} C" >&2
    failed=1
  }
  awk -v value="$start_temp1" -v limit="$MAX_START_TEMP_GPU1_C" 'BEGIN{exit !(value>limit)}' && {
    echo "GPU1 start temperature ${start_temp1} C exceeds ${MAX_START_TEMP_GPU1_C} C" >&2
    failed=1
  }

  local gpu_count
  gpu_count="$(nvidia-smi --query-gpu=index --format=csv,noheader | wc -l)"
  [[ "$gpu_count" -eq 2 ]] || {
    echo "Expected exactly 2 GPUs, found $gpu_count" >&2
    failed=1
  }

  local bad_limit
  bad_limit="$(nvidia-smi \
    --query-gpu=index,power.max_limit \
    --format=csv,noheader,nounits \
    | awk -F, '$2+0 < 600 {print $1}')"
  [[ -z "$bad_limit" ]] || {
    echo "GPU(s) without a 600 W maximum: $bad_limit" >&2
    failed=1
  }

  if lsof -ti "tcp:${GPU0_PORT}" >/dev/null 2>&1; then
    echo "GPU0 test port ${GPU0_PORT} is already in use" >&2
    failed=1
  fi

  if docker inspect "$GPU0_CONTAINER" >/dev/null 2>&1; then
    echo "Temporary container already exists: $GPU0_CONTAINER" >&2
    failed=1
  fi

  echo
  nvidia-smi \
    --query-gpu=index,name,power.draw,power.limit,temperature.gpu,temperature.gpu.tlimit,fan.speed,clocks.current.graphics,utilization.gpu,memory.used \
    --format=csv,noheader
  echo
  docker inspect "$SANCTUARY_CONTAINER" \
    --format 'GPU1 image={{.Image}} command={{json .Config.Cmd}}'

  if [[ "$failed" -ne 0 ]]; then
    log "CHECK FAILED"
    return 1
  fi

  log "CHECK PASS"
}

if [[ "$ACTION" == "check" ]]; then
  run_checks
  exit
fi

PREFLIGHT_SERVICE_GUARD_PID=""
declare -a PREFLIGHT_STOPPED_USER_SERVICES=()

preflight_restore() {
  local service
  set +e
  if [[ -n "$PREFLIGHT_SERVICE_GUARD_PID" ]]; then
    kill "$PREFLIGHT_SERVICE_GUARD_PID" 2>/dev/null
    wait "$PREFLIGHT_SERVICE_GUARD_PID" 2>/dev/null
  fi
  for service in "${PREFLIGHT_STOPPED_USER_SERVICES[@]:-}"; do
    [[ -n "$service" ]] && systemctl --user start "$service" >/dev/null 2>&1
  done
}

preflight_service_guard() {
  while true; do
    for service in "${CONFLICTING_USER_SERVICES[@]}"; do
      if systemctl --user is-active --quiet "$service"; then
        systemctl --user stop "$service" >/dev/null 2>&1 || return 1
      fi
    done
    sleep 1
  done
}

preflight_quiesce() {
  local service deadline sample temp0 util0 temp1 util1
  log "Preflight isolation: quiescing external GPU request sources"
  for service in "${CONFLICTING_USER_SERVICES[@]}"; do
    if systemctl --user is-active --quiet "$service"; then
      PREFLIGHT_STOPPED_USER_SERVICES+=("$service")
      systemctl --user stop "$service"
    fi
  done
  preflight_service_guard &
  PREFLIGHT_SERVICE_GUARD_PID=$!

  deadline=$((SECONDS + 900))
  while ((SECONDS < deadline)); do
    sample="$(nvidia-smi \
      --query-gpu=index,temperature.gpu,utilization.gpu \
      --format=csv,noheader,nounits)"
    read -r temp0 util0 < <(
      awk -F, '$1+0 == 0 {gsub(/ /,""); print $2,$3}' <<<"$sample"
    )
    read -r temp1 util1 < <(
      awk -F, '$1+0 == 1 {gsub(/ /,""); print $2,$3}' <<<"$sample"
    )
    if awk \
      -v t0="$temp0" -v u0="$util0" -v lim0="$MAX_START_TEMP_GPU0_C" \
      -v t1="$temp1" -v u1="$util1" -v lim1="$MAX_START_TEMP_GPU1_C" \
      'BEGIN {exit !(
        t0 <= lim0 && u0 == 0 &&
        t1 <= lim1 && u1 == 0
      )}'; then
      log "Preflight isolation ready: GPU0=${temp0}C/${util0}% GPU1=${temp1}C/${util1}%"
      return 0
    fi
    log "Preflight cooldown: GPU0=${temp0}C/${util0}% GPU1=${temp1}C/${util1}%"
    sleep 5
  done
  echo "Preflight isolation/cooldown exceeded 900 seconds" >&2
  return 1
}

trap preflight_restore EXIT INT TERM
preflight_quiesce
run_checks
sudo -n true 2>/dev/null || {
  echo "Sudo credentials are not primed. Run: sudo -v" >&2
  exit 1
}

mkdir -p "$OUT_ROOT"
STAMP="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
OUT="${OUT_ROOT}/${STAMP}-${TAG}"
mkdir -p "$OUT"

RUN_LOG="$OUT/run.log"
GPU_CSV="$OUT/gpu-telemetry.csv"
NVML_CLOCK_CSV="$OUT/gpu-nvml-clock.csv"
HOST_CSV="$OUT/host-telemetry.csv"
REQUESTS_CSV="$OUT/requests.csv"
EVENTS="$OUT/events.log"
PHASE_FILE="$OUT/.phase"
STOP_FILE="$OUT/.stop"
WORKERS_STOP_FILE="$OUT/.stop-workers"
ABORT_FILE="$OUT/.abort"
STOPPED_FILE="$OUT/stopped-containers.txt"
STOPPED_USER_SERVICES_FILE="$OUT/stopped-user-services.txt"
SUMMARY_JSON="$OUT/summary.json"
CHECKSUMS="$OUT/SHA256SUMS"
GPU0_PAYLOAD="$OUT/gpu0-payload.json"
GPU1_PAYLOAD="$OUT/gpu1-payload.json"
IMAGE_ID="$(docker inspect "$SANCTUARY_CONTAINER" --format '{{.Image}}')"
GPU1_MODEL_ID="$(curl -fsS "http://127.0.0.1:${GPU1_PORT}/v1/models" | jq -r '.data[0].id')"
GPU0_MODEL_ID="tower2-qwen27-gpu0"
ORIGINAL_LIMIT_0="$(nvidia-smi -i 0 --query-gpu=power.limit --format=csv,noheader,nounits | awk '{print $1}')"
ORIGINAL_LIMIT_1="$(nvidia-smi -i 1 --query-gpu=power.limit --format=csv,noheader,nounits | awk '{print $1}')"
read -r START_HW_THERMAL_0 START_HW_BRAKE_0 < <(
  nvidia-smi -i 0 \
    --query-gpu=clocks_event_reasons_counters.hw_thermal_slowdown,clocks_event_reasons_counters.hw_power_brake_slowdown \
    --format=csv,noheader,nounits | awk -F, '{gsub(/ /,""); print $1,$2}'
)
read -r START_HW_THERMAL_1 START_HW_BRAKE_1 < <(
  nvidia-smi -i 1 \
    --query-gpu=clocks_event_reasons_counters.hw_thermal_slowdown,clocks_event_reasons_counters.hw_power_brake_slowdown \
    --format=csv,noheader,nounits | awk -F, '{gsub(/ /,""); print $1,$2}'
)

exec > >(tee -a "$RUN_LOG") 2>&1

declare -a WORKER_PIDS=()
LOGGER_PID=""
HOST_LOGGER_PID=""
NVML_LOGGER_PID=""
SERVICE_GUARD_PID="$PREFLIGHT_SERVICE_GUARD_PID"
PREFLIGHT_SERVICE_GUARD_PID=""
GPU0_STARTED=0
WORKLOAD_STARTED=0
CLEANED_UP=0

stop_workers_now() {
  touch "$WORKERS_STOP_FILE"
  for pid in "${WORKER_PIDS[@]:-}"; do
    pkill -TERM -P "$pid" 2>/dev/null || true
    kill "$pid" 2>/dev/null || true
  done
  for pid in "${WORKER_PIDS[@]:-}"; do
    wait "$pid" 2>/dev/null || true
  done
  WORKER_PIDS=()
}

drain_workers() {
  local deadline=$((SECONDS + 120))
  local pid any_running

  touch "$WORKERS_STOP_FILE"
  while ((SECONDS < deadline)); do
    any_running=0
    for pid in "${WORKER_PIDS[@]:-}"; do
      if kill -0 "$pid" 2>/dev/null; then
        any_running=1
        break
      fi
    done
    ((any_running == 0)) && break
    sleep 2
  done

  any_running=0
  for pid in "${WORKER_PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      any_running=1
      break
    fi
  done
  if ((any_running == 1)); then
    log "Worker drain exceeded 120s; terminating remaining clients"
    stop_workers_now
    return
  fi

  for pid in "${WORKER_PIDS[@]:-}"; do
    wait "$pid" 2>/dev/null || true
  done
  WORKER_PIDS=()
}

cleanup() {
  local rc=$?
  if [[ "$CLEANED_UP" -eq 1 ]]; then
    return
  fi
  CLEANED_UP=1
  set +e
  touch "$STOP_FILE"
  stop_workers_now
  [[ -n "$LOGGER_PID" ]] && kill "$LOGGER_PID" 2>/dev/null
  [[ -n "$HOST_LOGGER_PID" ]] && kill "$HOST_LOGGER_PID" 2>/dev/null
  [[ -n "$NVML_LOGGER_PID" ]] && kill "$NVML_LOGGER_PID" 2>/dev/null
  [[ -n "$SERVICE_GUARD_PID" ]] && kill "$SERVICE_GUARD_PID" 2>/dev/null

  [[ -n "$LOGGER_PID" ]] && wait "$LOGGER_PID" 2>/dev/null
  [[ -n "$HOST_LOGGER_PID" ]] && wait "$HOST_LOGGER_PID" 2>/dev/null
  [[ -n "$NVML_LOGGER_PID" ]] && wait "$NVML_LOGGER_PID" 2>/dev/null
  [[ -n "$SERVICE_GUARD_PID" ]] && wait "$SERVICE_GUARD_PID" 2>/dev/null

  if [[ "$GPU0_STARTED" -eq 1 ]]; then
    docker stop -t 20 "$GPU0_CONTAINER" >/dev/null 2>&1
  fi

  if [[ "$rc" -ne 0 && "$WORKLOAD_STARTED" -eq 1 ]]; then
    log "Interrupted/failed workload; restarting Sanctuary to clear admitted requests"
    docker restart -t 30 "$SANCTUARY_CONTAINER" >/dev/null 2>&1
    for _ in $(seq 1 90); do
      curl -fsS -m 3 "http://127.0.0.1:${GPU1_PORT}/v1/models" >/dev/null 2>&1 && break
      sleep 2
    done
  fi

  sudo -n nvidia-smi -i 0 -pl "$ORIGINAL_LIMIT_0" >/dev/null 2>&1
  sudo -n nvidia-smi -i 1 -pl "$ORIGINAL_LIMIT_1" >/dev/null 2>&1

  if [[ -f "$STOPPED_FILE" ]]; then
    while IFS= read -r container; do
      [[ -n "$container" ]] && docker start "$container" >/dev/null 2>&1
    done < "$STOPPED_FILE"
  fi
  if [[ -f "$STOPPED_USER_SERVICES_FILE" ]]; then
    while IFS= read -r service; do
      [[ -n "$service" ]] && systemctl --user start "$service" >/dev/null 2>&1
    done < "$STOPPED_USER_SERVICES_FILE"
  fi

  rm -f "$PHASE_FILE" "$STOP_FILE" "$WORKERS_STOP_FILE" "$ABORT_FILE"
  log "Cleanup complete; original GPU services and power limits restored"
  (
    cd "$OUT"
    find . -maxdepth 1 -type f ! -name SHA256SUMS -printf '%P\n' \
      | sort \
      | xargs -r sha256sum
  ) > "$CHECKSUMS"
  exit "$rc"
}

: > "$STOPPED_FILE"
: > "$STOPPED_USER_SERVICES_FILE"
for service in "${PREFLIGHT_STOPPED_USER_SERVICES[@]:-}"; do
  [[ -n "$service" ]] && echo "$service" >> "$STOPPED_USER_SERVICES_FILE"
done
trap cleanup EXIT INT TERM

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Heavy fleet lock is held: $LOCK_FILE" >&2
  exit 1
fi

log "Output: $OUT"
printf 'setup\n' > "$PHASE_FILE"
printf 'ts_iso,event\n%s,run-created\n' "$(date -u +%FT%T.%3NZ)" > "$EVENTS"
printf 'ts_iso,gpu,phase,http_status,duration_s,response_bytes\n' > "$REQUESTS_CSV"

jq -n \
  --arg tag "$TAG" \
  --arg cell_id "$CELL_ID" \
  --argjson replicate "$REPLICATE" \
  --arg started_at "$(date -u +%FT%T.%3NZ)" \
  --arg image_id "$IMAGE_ID" \
  --arg model_path "$MODEL_PATH" \
  --arg gpu1_model_id "$GPU1_MODEL_ID" \
  --argjson duration_s "$DURATION_S" \
  --argjson warmup_s "$WARMUP_S" \
  --argjson cooldown_s "$COOLDOWN_S" \
  --argjson concurrency_per_gpu "$CONCURRENCY" \
  --argjson concurrency_gpu0 "$CONCURRENCY_GPU0" \
  --argjson concurrency_gpu1 "$CONCURRENCY_GPU1" \
  --argjson max_tokens "$MAX_TOKENS" \
  --argjson min_warmup_power_gpu0_w "$MIN_WARMUP_POWER_GPU0_W" \
  --argjson min_warmup_power_gpu1_w "$MIN_WARMUP_POWER_GPU1_W" \
  --argjson gpu0_power_limit_w "$GPU0_POWER_LIMIT_W" \
  --argjson gpu1_power_limit_w "$GPU1_POWER_LIMIT_W" \
  --argjson gpu_abort_c "$GPU_ABORT_C" \
  --argjson max_start_temp_gpu0_c "$MAX_START_TEMP_GPU0_C" \
  --argjson max_start_temp_gpu1_c "$MAX_START_TEMP_GPU1_C" \
  --argjson max_idle_power_gpu0_w "$MAX_IDLE_POWER_GPU0_W" \
  --argjson max_idle_power_gpu1_w "$MAX_IDLE_POWER_GPU1_W" \
  --argjson telemetry_interval_ms "$TELEMETRY_INTERVAL_MS" \
  --argjson nvml_clock_base_ms "$NVML_CLOCK_BASE_MS" \
  --argjson nvml_clock_jitter_ms "$NVML_CLOCK_JITTER_MS" \
  --arg ambient_c "$AMBIENT_C" \
  '{
    tag:$tag,
    cell_id:$cell_id,
    replicate:$replicate,
    started_at:$started_at,
    model_path:$model_path,
    image_id:$image_id,
    gpu1_model_id:$gpu1_model_id,
    duration_s:$duration_s,
    warmup_s:$warmup_s,
    cooldown_s:$cooldown_s,
    concurrency_per_gpu:$concurrency_per_gpu,
    concurrency_gpu0:$concurrency_gpu0,
    concurrency_gpu1:$concurrency_gpu1,
    max_tokens:$max_tokens,
    min_warmup_power_gpu0_w:$min_warmup_power_gpu0_w,
    min_warmup_power_gpu1_w:$min_warmup_power_gpu1_w,
    gpu0_power_limit_w:$gpu0_power_limit_w,
    gpu1_power_limit_w:$gpu1_power_limit_w,
    gpu_abort_c:$gpu_abort_c,
    max_start_temp_gpu0_c:$max_start_temp_gpu0_c,
    max_start_temp_gpu1_c:$max_start_temp_gpu1_c,
    max_idle_power_gpu0_w:$max_idle_power_gpu0_w,
    max_idle_power_gpu1_w:$max_idle_power_gpu1_w,
    telemetry_interval_ms:$telemetry_interval_ms,
    nvml_clock_base_ms:$nvml_clock_base_ms,
    nvml_clock_jitter_ms:$nvml_clock_jitter_ms,
    ambient_c:(if $ambient_c == "" then null else ($ambient_c | tonumber) end)
  }' > "$OUT/run-config.json"

nvidia-smi -q > "$OUT/nvidia-before.txt"
nvidia-smi -q -x > "$OUT/nvidia-before.xml"
uname -a > "$OUT/host-before.txt"
docker ps --no-trunc > "$OUT/containers-before.txt"
systemctl --user --no-pager status "${CONFLICTING_USER_SERVICES[@]}" > "$OUT/user-services-before.txt" 2>&1 || true
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory \
  --format=csv > "$OUT/gpu-processes-before.csv"
curl -fsS "http://127.0.0.1:${GPU1_PORT}/metrics" > "$OUT/gpu1-vllm-metrics-before.txt"
docker inspect "$SANCTUARY_CONTAINER" > "$OUT/sanctuary-inspect.json"

log "Stopping GPU containers that conflict with an isolated GPU0 replica"
for service in "${CONFLICTING_USER_SERVICES[@]}"; do
  if systemctl --user is-active --quiet "$service"; then
    echo "$service" >> "$STOPPED_USER_SERVICES_FILE"
    systemctl --user stop "$service"
  fi
done
service_guard() {
  while [[ ! -f "$STOP_FILE" ]]; do
    for service in "${CONFLICTING_USER_SERVICES[@]}"; do
      if systemctl --user is-active --quiet "$service"; then
        printf '%s,service-guard-stopped-%s\n' \
          "$(date -u +%FT%T.%3NZ)" "$service" >> "$EVENTS"
        systemctl --user stop "$service" || {
          printf '%s service guard failed to stop %s\n' \
            "$(date -u +%FT%T.%3NZ)" "$service" > "$ABORT_FILE"
          return 1
        }
      fi
    done
    sleep 1
  done
}
if [[ -n "$SERVICE_GUARD_PID" ]]; then
  kill "$SERVICE_GUARD_PID" 2>/dev/null || true
  wait "$SERVICE_GUARD_PID" 2>/dev/null || true
fi
service_guard &
SERVICE_GUARD_PID=$!
for container in "${CONFLICTING_CONTAINERS[@]}"; do
  if [[ "$(docker inspect "$container" --format '{{.State.Running}}' 2>/dev/null || true)" == "true" ]]; then
    echo "$container" >> "$STOPPED_FILE"
    docker stop -t 30 "$container"
  fi
done

sleep 3
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory \
  --format=csv > "$OUT/gpu-processes-isolated.csv"
pgrep -f 'memory-core-local-embedding-worker[.]js' >/dev/null && {
  echo "OpenClaw embedding worker survived GPU isolation" >&2
  exit 1
}
sanctuary_model_ok || {
  echo "Sanctuary Qwen27 on GPU1 became unhealthy during isolation" >&2
  exit 1
}

gpu0_used="$(nvidia-smi -i 0 --query-gpu=memory.used --format=csv,noheader,nounits | awk '{print $1}')"
if ((gpu0_used > 2048)); then
  echo "GPU0 still has ${gpu0_used} MiB allocated after isolation; refusing to continue" >&2
  nvidia-smi
  exit 1
fi

log "Setting GPU0/bottom to ${GPU0_POWER_LIMIT_W} W and GPU1/top to ${GPU1_POWER_LIMIT_W} W"
sudo -n nvidia-smi -i 0 -pl "$GPU0_POWER_LIMIT_W"
sudo -n nvidia-smi -i 1 -pl "$GPU1_POWER_LIMIT_W"

if ((CONCURRENCY_GPU0 > 0)); then
  log "Launching identical Qwen3.6-27B AWQ-INT4 vLLM replica on GPU0"
  docker run -d --rm \
    --name "$GPU0_CONTAINER" \
    --gpus '"device=0"' \
    -v "${MODEL_SOURCE}:/models:ro" \
    -p "127.0.0.1:${GPU0_PORT}:8000" \
    "$IMAGE_ID" \
    --model "$MODEL_PATH" \
    --served-model-name "$GPU0_MODEL_ID" \
    --host 0.0.0.0 \
    --port 8000 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.92 \
    --max-model-len 262144 \
    --trust-remote-code \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_coder
  GPU0_STARTED=1

  log "Waiting for GPU0 vLLM readiness"
  ready=0
  for _ in $(seq 1 180); do
    if [[ "$(docker inspect "$GPU0_CONTAINER" --format '{{.State.Running}}' 2>/dev/null || true)" != "true" ]]; then
      docker logs "$GPU0_CONTAINER" 2>&1 | tail -100
      echo "GPU0 vLLM container exited during startup" >&2
      exit 1
    fi
    if curl -fsS -m 3 "http://127.0.0.1:${GPU0_PORT}/v1/models" \
        | jq -e --arg id "$GPU0_MODEL_ID" '.data[] | select(.id == $id)' >/dev/null; then
      ready=1
      break
    fi
    sleep 5
  done
  [[ "$ready" -eq 1 ]] || {
    docker logs "$GPU0_CONTAINER" 2>&1 | tail -100
    echo "GPU0 vLLM did not become ready" >&2
    exit 1
  }
else
  log "GPU0 concurrency is 0; leaving GPU0 isolated and idle"
fi

PROMPT="Write a continuous, highly detailed technical analysis of a hypothetical datacenter cooling incident. Keep generating dense explanatory prose, calculations, diagnostics, and remediation steps until the token limit."
jq -n \
  --arg model "$GPU0_MODEL_ID" \
  --arg prompt "$PROMPT" \
  --argjson max_tokens "$MAX_TOKENS" \
  '{model:$model,messages:[{role:"user",content:$prompt}],max_tokens:$max_tokens,temperature:0.7,stream:false}' \
  > "$GPU0_PAYLOAD"
jq -n \
  --arg model "$GPU1_MODEL_ID" \
  --arg prompt "$PROMPT" \
  --argjson max_tokens "$MAX_TOKENS" \
  '{model:$model,messages:[{role:"user",content:$prompt}],max_tokens:$max_tokens,temperature:0.7,stream:false}' \
  > "$GPU1_PAYLOAD"

gpu_logger() {
  local interval_ns next_sample_ns now_ns sleep_s
  interval_ns=$((TELEMETRY_INTERVAL_MS * 1000000))
  next_sample_ns="$(date +%s%N)"
  echo "ts_wall_iso,ts_mono_s,phase,index,nvidia_timestamp,temp_gpu_c,temp_memory_c,power_avg_w,power_instant_w,power_limit_w,enforced_power_limit_w,graphics_clock_mhz,sm_clock_mhz,memory_clock_mhz,gpu_util_pct,memory_util_pct,fan_pct,pstate,memory_used_mib,sw_power_cap,hw_thermal_slowdown,hw_power_brake_slowdown,sw_thermal_slowdown,temp_tlimit_margin_c,sw_power_cap_counter_us,sw_thermal_slowdown_counter_us,hw_thermal_slowdown_counter_us,hw_power_brake_counter_us" > "$GPU_CSV"
  while [[ ! -f "$STOP_FILE" ]]; do
    wall="$(date -u +%FT%T.%3NZ)"
    mono="$(awk 'BEGIN{getline x < "/proc/uptime"; split(x,a," "); print a[1]}')"
    phase="$(cat "$PHASE_FILE" 2>/dev/null || echo unknown)"
    sample="$(telemetry_probe)"
    awk -v w="$wall" -v m="$mono" -v p="$phase" \
      '{print w "," m "," p "," $0}' <<<"$sample" >> "$GPU_CSV"
    if awk -F, -v limit="$GPU_ABORT_C" '
        {
          gsub(/ /,"",$3)
          gsub(/^[ \t]+|[ \t]+$/,"",$18)
          gsub(/^[ \t]+|[ \t]+$/,"",$19)
          if ($3+0 >= limit || $18 == "Active" || $19 == "Active") hit=1
        }
        END {exit (hit ? 0 : 1)}
      ' <<<"$sample"; then
      printf '%s phase=%s limit=%s sample=%s\n' \
        "$wall" "$phase" "$GPU_ABORT_C" "$(tr '\n' ';' <<<"$sample")" \
        > "$ABORT_FILE"
    fi
    next_sample_ns=$((next_sample_ns + interval_ns))
    now_ns="$(date +%s%N)"
    if ((next_sample_ns > now_ns)); then
      sleep_s="$(awk -v ns="$((next_sample_ns - now_ns))" 'BEGIN{printf "%.6f",ns/1000000000}')"
      sleep "$sleep_s"
    else
      next_sample_ns="$now_ns"
    fi
  done
}

host_logger() {
  echo "ts_wall_iso,ts_mono_s,phase,ambient_c,cpu_tctl_c,cpu_ccd_max_c,cpu_avg_mhz,nvme_max_c" > "$HOST_CSV"
  while [[ ! -f "$STOP_FILE" ]]; do
    wall="$(date -u +%FT%T.%3NZ)"
    mono="$(awk 'BEGIN{getline x < "/proc/uptime"; split(x,a," "); print a[1]}')"
    phase="$(cat "$PHASE_FILE" 2>/dev/null || echo unknown)"
    sensor_text="$(sensors 2>/dev/null)"
    tctl="$(awk '/Tctl/{v=$2; gsub(/[+°C]/,"",v); print v; exit}' <<<"$sensor_text")"
    ccd="$(awk '/Tccd/{v=$2; gsub(/[+°C]/,"",v); if(v+0>m)m=v+0} END{if(m)printf "%.1f",m}' <<<"$sensor_text")"
    nvme="$(awk '/^Composite/{v=$2; gsub(/[+°C]/,"",v); if(v+0>m)m=v+0} END{if(m)printf "%.1f",m}' <<<"$sensor_text")"
    mhz="$(awk '/cpu MHz/{s+=$4;n++} END{printf "%.0f",(n?s/n:0)}' /proc/cpuinfo)"
    printf '%s,%s,%s,%s,%s,%s,%s,%s\n' "$wall" "$mono" "$phase" "$AMBIENT_C" "$tctl" "$ccd" "$mhz" "$nvme" >> "$HOST_CSV"
    sleep 1
  done
}

request_worker() {
  local gpu="$1" endpoint="$2" payload="$3"
  while [[ ! -f "$WORKERS_STOP_FILE" ]]; do
    phase="$(cat "$PHASE_FILE" 2>/dev/null || echo unknown)"
    if ! result="$(curl -sS \
        --connect-timeout 5 \
        --max-time 600 \
        -o /dev/null \
        -w '%{http_code},%{time_total},%{size_download}' \
        -X POST "${endpoint}/v1/chat/completions" \
        -H 'Content-Type: application/json' \
        --data-binary "@${payload}" 2>/dev/null)"; then
      result="000,0,0"
    fi
    printf '%s,%s,%s,%s\n' "$(date -u +%FT%T.%3NZ)" "$gpu" "$phase" "$result" >> "$REQUESTS_CSV"
  done
}

log "Starting ${TELEMETRY_INTERVAL_MS} ms GPU telemetry; workers GPU0=${CONCURRENCY_GPU0} GPU1=${CONCURRENCY_GPU1}"
gpu_logger &
LOGGER_PID=$!
host_logger &
HOST_LOGGER_PID=$!
python3 "$(dirname "$0")/nvml-clock-logger.py" \
  --output "$NVML_CLOCK_CSV" \
  --phase-file "$PHASE_FILE" \
  --stop-file "$STOP_FILE" \
  --base-ms "$NVML_CLOCK_BASE_MS" \
  --jitter-ms "$NVML_CLOCK_JITTER_MS" &
NVML_LOGGER_PID=$!
for ((worker=0; worker<CONCURRENCY_GPU0; worker++)); do
  request_worker gpu0 "http://127.0.0.1:${GPU0_PORT}" "$GPU0_PAYLOAD" &
  WORKER_PIDS+=("$!")
done
for ((worker=0; worker<CONCURRENCY_GPU1; worker++)); do
  request_worker gpu1 "http://127.0.0.1:${GPU1_PORT}" "$GPU1_PAYLOAD" &
  WORKER_PIDS+=("$!")
done
WORKLOAD_STARTED=1

printf 'warmup\n' > "$PHASE_FILE"
printf '%s,warmup-started\n' "$(date -u +%FT%T.%3NZ)" >> "$EVENTS"
log "Warm-up started (${WARMUP_S}s)"
sleep "$WARMUP_S"

kill -0 "$NVML_LOGGER_PID" 2>/dev/null || {
  echo "Independent NVML clock logger exited during warm-up" >&2
  exit 1
}

gate_window_s=$((WARMUP_S / 4))
((gate_window_s < 5)) && gate_window_s=5
((gate_window_s > 30)) && gate_window_s=30
read -r warm0 warm1 < <(
  awk -F, -v window="$gate_window_s" '
    FNR == NR {
      if ($3 == "warmup" && $2+0 > max_mono) max_mono=$2+0
      next
    }
    $3 == "warmup" && $2+0 >= max_mono-window {
      gsub(/ /,"",$4); gsub(/ /,"",$8)
      if ($4 == 0 && $8+0 > 0) {s0+=$8; n0++}
      if ($4 == 1 && $8+0 > 0) {s1+=$8; n1++}
    }
    END {printf "%.2f %.2f\n",(n0?s0/n0:0),(n1?s1/n1:0)}
  ' "$GPU_CSV" "$GPU_CSV"
)
log "Trailing ${gate_window_s}s warm-up mean board power: GPU0=${warm0}W GPU1=${warm1}W"
awk -v a="$warm0" -v b="$warm1" -v min0="$MIN_WARMUP_POWER_GPU0_W" -v min1="$MIN_WARMUP_POWER_GPU1_W" \
  'BEGIN{exit !((a+0)>=min0 && (b+0)>=min1)}' || {
    echo "Saturation gate failed: GPU0 must average at least ${MIN_WARMUP_POWER_GPU0_W} W and GPU1 at least ${MIN_WARMUP_POWER_GPU1_W} W during warm-up" >&2
    exit 1
  }
sanctuary_test_load_isolated || {
  echo "Workload-isolation gate failed: Sanctuary exceeds the controlled GPU1 worker count or has a wait queue" >&2
  exit 1
}
pgrep -f 'memory-core-local-embedding-worker[.]js' >/dev/null && {
  echo "Workload-isolation gate failed: OpenClaw embedding worker is active" >&2
  exit 1
}
if ((CONCURRENCY_GPU0 == 0)); then
  awk -v value="$warm0" -v limit="$MAX_IDLE_POWER_GPU0_W" 'BEGIN{exit !(value>limit)}' && {
    echo "Idle-isolation gate failed: GPU0 averaged ${warm0} W (limit ${MAX_IDLE_POWER_GPU0_W} W)" >&2
    exit 1
  }
fi
if ((CONCURRENCY_GPU1 == 0)); then
  awk -v value="$warm1" -v limit="$MAX_IDLE_POWER_GPU1_W" 'BEGIN{exit !(value>limit)}' && {
    echo "Idle-isolation gate failed: GPU1 averaged ${warm1} W (limit ${MAX_IDLE_POWER_GPU1_W} W)" >&2
    exit 1
  }
fi

printf 'measured\n' > "$PHASE_FILE"
printf '%s,measured-started\n' "$(date -u +%FT%T.%3NZ)" >> "$EVENTS"
log "Measured GPU0=${GPU0_POWER_LIMIT_W} W / GPU1=${GPU1_POWER_LIMIT_W} W run started (${DURATION_S}s)"

started_epoch="$(date +%s)"
deadline=$((started_epoch + DURATION_S))
next_update=$((started_epoch + 60))
while (( $(date +%s) < deadline )); do
  sleep 5

  if [[ -s "$ABORT_FILE" ]]; then
    echo "Emergency cutoff requested by 1 Hz telemetry: $(cat "$ABORT_FILE")" >&2
    exit 1
  fi

  sanctuary_model_ok || {
    echo "GPU1 Sanctuary endpoint became unhealthy" >&2
    exit 1
  }
  sanctuary_test_load_isolated || {
    echo "Workload-isolation cutoff: Sanctuary exceeds the controlled GPU1 worker count or has a wait queue" >&2
    exit 1
  }
  pgrep -f 'memory-core-local-embedding-worker[.]js' >/dev/null && {
    echo "Workload-isolation cutoff: OpenClaw embedding worker became active" >&2
    exit 1
  }
  if ((CONCURRENCY_GPU0 > 0)); then
    [[ "$(docker inspect "$GPU0_CONTAINER" --format '{{.State.Running}}' 2>/dev/null || true)" == "true" ]] || {
      echo "GPU0 vLLM container exited" >&2
      exit 1
    }
  fi

  current_max_temp="$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | awk 'm<$1{m=$1}END{print m+0}')"
  awk -v t="$current_max_temp" -v limit="$GPU_ABORT_C" 'BEGIN{exit !(t>=limit)}' && {
    echo "Emergency cutoff: GPU temperature reached ${current_max_temp} C (limit ${GPU_ABORT_C} C)" >&2
    exit 1
  }
  read -r current_power0 current_power1 < <(
    nvidia-smi --query-gpu=power.draw.average --format=csv,noheader,nounits \
      | awk 'NR==1{a=$1} NR==2{b=$1} END{print a+0,b+0}'
  )
  if ((CONCURRENCY_GPU0 == 0)); then
    awk -v value="$current_power0" -v limit="$MAX_IDLE_POWER_GPU0_W" 'BEGIN{exit !(value>limit)}' && {
      echo "Isolation cutoff: idle GPU0 reached ${current_power0} W (limit ${MAX_IDLE_POWER_GPU0_W} W)" >&2
      exit 1
    }
  fi
  if ((CONCURRENCY_GPU1 == 0)); then
    awk -v value="$current_power1" -v limit="$MAX_IDLE_POWER_GPU1_W" 'BEGIN{exit !(value>limit)}' && {
      echo "Isolation cutoff: idle GPU1 reached ${current_power1} W (limit ${MAX_IDLE_POWER_GPU1_W} W)" >&2
      exit 1
    }
  fi

  if nvidia-smi \
      --query-gpu=clocks_event_reasons.hw_thermal_slowdown,clocks_event_reasons.hw_power_brake_slowdown \
      --format=csv,noheader \
      | awk -F, '
          {
            gsub(/^[ \t]+|[ \t]+$/,"",$1)
            gsub(/^[ \t]+|[ \t]+$/,"",$2)
            if ($1 == "Active" || $2 == "Active") hit=1
          }
          END {exit (hit ? 0 : 1)}
        '; then
    echo "Emergency cutoff: hardware thermal slowdown or power-brake event became active" >&2
    exit 1
  fi

  if nvidia-smi \
      --query-gpu=index,clocks_event_reasons_counters.hw_thermal_slowdown,clocks_event_reasons_counters.hw_power_brake_slowdown \
      --format=csv,noheader,nounits \
      | awk -F, \
          -v h0="$START_HW_THERMAL_0" -v b0="$START_HW_BRAKE_0" \
          -v h1="$START_HW_THERMAL_1" -v b1="$START_HW_BRAKE_1" '
          {
            for (i=1;i<=NF;i++) gsub(/ /,"",$i)
            if ($1 == 0 && ($2+0 > h0+0 || $3+0 > b0+0)) hit=1
            if ($1 == 1 && ($2+0 > h1+0 || $3+0 > b1+0)) hit=1
          }
          END {exit (hit ? 0 : 1)}
        '; then
    echo "Emergency cutoff: cumulative hardware thermal or power-brake counter increased" >&2
    exit 1
  fi

  now="$(date +%s)"
  if ((now >= next_update)); then
    elapsed=$((now - started_epoch))
    snapshot="$(nvidia-smi \
      --query-gpu=index,power.draw.average,temperature.gpu,temperature.gpu.tlimit,fan.speed,clocks.current.graphics,utilization.gpu,clocks_event_reasons.sw_power_cap,clocks_event_reasons.sw_thermal_slowdown,clocks_event_reasons.hw_thermal_slowdown \
      --format=csv,noheader)"
    log "Progress ${elapsed}/${DURATION_S}s"
    printf '%s\n' "$snapshot"
    next_update=$((next_update + 60))
  fi
done

printf '%s,measured-finished\n' "$(date -u +%FT%T.%3NZ)" >> "$EVENTS"
printf 'drain\n' > "$PHASE_FILE"
log "Measured run complete; draining admitted requests"
drain_workers
printf 'cooldown\n' > "$PHASE_FILE"
log "Requests drained; logging ${COOLDOWN_S}s cooldown"
sleep "$COOLDOWN_S"
touch "$STOP_FILE"
wait "$LOGGER_PID" "$HOST_LOGGER_PID" "$NVML_LOGGER_PID" 2>/dev/null || true
LOGGER_PID=""
HOST_LOGGER_PID=""
NVML_LOGGER_PID=""

nvidia-smi -q > "$OUT/nvidia-after.txt"
nvidia-smi -q -x > "$OUT/nvidia-after.xml"
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory \
  --format=csv > "$OUT/gpu-processes-after.csv"
curl -fsS "http://127.0.0.1:${GPU1_PORT}/metrics" > "$OUT/gpu1-vllm-metrics-after.txt" || true
if ((GPU0_STARTED == 1)); then
  docker logs "$GPU0_CONTAINER" > "$OUT/gpu0-vllm.log" 2>&1 || true
fi

python3 "$(dirname "$0")/summarize-dual-vllm.py" \
  "$GPU_CSV" "$HOST_CSV" "$REQUESTS_CSV" "$SUMMARY_JSON" \
  "$OUT/nvidia-before.txt" "$OUT/nvidia-after.txt" \
  "$OUT/gpu1-vllm-metrics-before.txt" "$OUT/gpu1-vllm-metrics-after.txt"

jq -e '
  .workload_isolation.success_delta_matches_controlled_log == true and
  .workload_isolation.controlled_errors_all_gpus_all_phases == 0 and
  .quality_gates.internal_admissible_candidate == true
' "$SUMMARY_JSON" >/dev/null || {
  echo "Post-run validation gate failed; see ${SUMMARY_JSON}" >&2
  exit 1
}

log "PASS — summary: $SUMMARY_JSON"
cat "$SUMMARY_JSON"
