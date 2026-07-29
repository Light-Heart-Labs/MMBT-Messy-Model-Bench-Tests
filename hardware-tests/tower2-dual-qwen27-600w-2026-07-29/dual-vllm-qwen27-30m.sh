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
DURATION_S=1800
WARMUP_S=120
COOLDOWN_S=60
CONCURRENCY=32
MAX_TOKENS=1024
MIN_WARMUP_POWER_W=570
GPU_ABORT_C=92
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

usage() {
  cat <<'EOF'
Usage:
  dual-vllm-qwen27-30m.sh [--check]
  dual-vllm-qwen27-30m.sh --run [options]

Options:
  --check                  Readiness checks only (default; no changes)
  --run                    Run the guarded saturation test
  --tag NAME               Output tag
  --duration SECONDS       Measured duration (default: 1800)
  --warmup SECONDS         Saturation warm-up (default: 120)
  --cooldown SECONDS       Logged cooldown (default: 60)
  --concurrency N          Concurrent requests per GPU (default: 32)
  --max-tokens N           Maximum generated tokens/request (default: 1024)
  --min-power W            Required warm-up mean per GPU (default: 570)
  --gpu-abort-c C          Emergency GPU-temperature cutoff (default: 92)

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
    --duration) DURATION_S="${2:?missing value for --duration}"; shift 2 ;;
    --warmup) WARMUP_S="${2:?missing value for --warmup}"; shift 2 ;;
    --cooldown) COOLDOWN_S="${2:?missing value for --cooldown}"; shift 2 ;;
    --concurrency) CONCURRENCY="${2:?missing value for --concurrency}"; shift 2 ;;
    --max-tokens) MAX_TOKENS="${2:?missing value for --max-tokens}"; shift 2 ;;
    --min-power) MIN_WARMUP_POWER_W="${2:?missing value for --min-power}"; shift 2 ;;
    --gpu-abort-c) GPU_ABORT_C="${2:?missing value for --gpu-abort-c}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for value in DURATION_S WARMUP_S COOLDOWN_S CONCURRENCY MAX_TOKENS; do
  [[ "${!value}" =~ ^[1-9][0-9]*$ ]] || {
    echo "$value must be a positive integer" >&2
    exit 2
  }
done
[[ "$MIN_WARMUP_POWER_W" =~ ^[0-9]+([.][0-9]+)?$ ]] || {
  echo "MIN_WARMUP_POWER_W must be numeric" >&2
  exit 2
}
[[ "$GPU_ABORT_C" =~ ^[0-9]+([.][0-9]+)?$ ]] || {
  echo "GPU_ABORT_C must be numeric" >&2
  exit 2
}
[[ "$TAG" =~ ^[A-Za-z0-9._-]+$ ]] || {
  echo "TAG may contain only letters, digits, dot, underscore, and dash" >&2
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

telemetry_probe() {
  nvidia-smi \
    --query-gpu=index,timestamp,temperature.gpu,temperature.memory,power.draw.average,power.draw.instant,power.limit,enforced.power.limit,clocks.current.graphics,clocks.current.sm,clocks.current.memory,utilization.gpu,utilization.memory,fan.speed,pstate,memory.used,clocks_event_reasons.sw_power_cap,clocks_event_reasons.hw_thermal_slowdown,clocks_event_reasons.hw_power_brake_slowdown,clocks_event_reasons.sw_thermal_slowdown \
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

  telemetry_probe >/dev/null || {
    echo "Required NVIDIA telemetry fields are unavailable" >&2
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
    --query-gpu=index,name,power.draw,power.limit,temperature.gpu,clocks.current.graphics,utilization.gpu,memory.used \
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
HOST_CSV="$OUT/host-telemetry.csv"
REQUESTS_CSV="$OUT/requests.csv"
EVENTS="$OUT/events.log"
PHASE_FILE="$OUT/.phase"
STOP_FILE="$OUT/.stop"
WORKERS_STOP_FILE="$OUT/.stop-workers"
ABORT_FILE="$OUT/.abort"
STOPPED_FILE="$OUT/stopped-containers.txt"
SUMMARY_JSON="$OUT/summary.json"
GPU0_PAYLOAD="$OUT/gpu0-payload.json"
GPU1_PAYLOAD="$OUT/gpu1-payload.json"
IMAGE_ID="$(docker inspect "$SANCTUARY_CONTAINER" --format '{{.Image}}')"
GPU1_MODEL_ID="$(curl -fsS "http://127.0.0.1:${GPU1_PORT}/v1/models" | jq -r '.data[0].id')"
GPU0_MODEL_ID="tower2-qwen27-gpu0"
ORIGINAL_LIMIT_0="$(nvidia-smi -i 0 --query-gpu=power.limit --format=csv,noheader,nounits | awk '{print $1}')"
ORIGINAL_LIMIT_1="$(nvidia-smi -i 1 --query-gpu=power.limit --format=csv,noheader,nounits | awk '{print $1}')"

exec > >(tee -a "$RUN_LOG") 2>&1

declare -a WORKER_PIDS=()
LOGGER_PID=""
HOST_LOGGER_PID=""
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

  [[ -n "$LOGGER_PID" ]] && wait "$LOGGER_PID" 2>/dev/null
  [[ -n "$HOST_LOGGER_PID" ]] && wait "$HOST_LOGGER_PID" 2>/dev/null

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

  rm -f "$PHASE_FILE" "$STOP_FILE" "$WORKERS_STOP_FILE" "$ABORT_FILE"
  log "Cleanup complete; original GPU services and power limits restored"
  exit "$rc"
}
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
  --arg started_at "$(date -u +%FT%T.%3NZ)" \
  --arg image_id "$IMAGE_ID" \
  --arg model_path "$MODEL_PATH" \
  --arg gpu1_model_id "$GPU1_MODEL_ID" \
  --argjson duration_s "$DURATION_S" \
  --argjson warmup_s "$WARMUP_S" \
  --argjson cooldown_s "$COOLDOWN_S" \
  --argjson concurrency_per_gpu "$CONCURRENCY" \
  --argjson max_tokens "$MAX_TOKENS" \
  --argjson min_warmup_power_w "$MIN_WARMUP_POWER_W" \
  --argjson gpu_abort_c "$GPU_ABORT_C" \
  '{
    tag:$tag,
    started_at:$started_at,
    model_path:$model_path,
    image_id:$image_id,
    gpu1_model_id:$gpu1_model_id,
    duration_s:$duration_s,
    warmup_s:$warmup_s,
    cooldown_s:$cooldown_s,
    concurrency_per_gpu:$concurrency_per_gpu,
    max_tokens:$max_tokens,
    min_warmup_power_w:$min_warmup_power_w,
    gpu_abort_c:$gpu_abort_c
  }' > "$OUT/run-config.json"

nvidia-smi -q > "$OUT/nvidia-before.txt"
docker inspect "$SANCTUARY_CONTAINER" > "$OUT/sanctuary-inspect.json"

log "Stopping GPU containers that conflict with an isolated GPU0 replica"
: > "$STOPPED_FILE"
for container in "${CONFLICTING_CONTAINERS[@]}"; do
  if [[ "$(docker inspect "$container" --format '{{.State.Running}}' 2>/dev/null || true)" == "true" ]]; then
    echo "$container" >> "$STOPPED_FILE"
    docker stop -t 30 "$container"
  fi
done

sleep 3
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

log "Setting both GPU power limits to 600 W"
sudo -n nvidia-smi -i 0 -pl 600
sudo -n nvidia-smi -i 1 -pl 600

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
  echo "ts_wall_iso,ts_mono_s,phase,index,nvidia_timestamp,temp_gpu_c,temp_memory_c,power_avg_w,power_instant_w,power_limit_w,enforced_power_limit_w,graphics_clock_mhz,sm_clock_mhz,memory_clock_mhz,gpu_util_pct,memory_util_pct,fan_pct,pstate,memory_used_mib,sw_power_cap,hw_thermal_slowdown,hw_power_brake_slowdown,sw_thermal_slowdown" > "$GPU_CSV"
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
    sleep 1
  done
}

host_logger() {
  echo "ts_wall_iso,ts_mono_s,phase,cpu_tctl_c,cpu_ccd_max_c,cpu_avg_mhz,nvme_max_c" > "$HOST_CSV"
  while [[ ! -f "$STOP_FILE" ]]; do
    wall="$(date -u +%FT%T.%3NZ)"
    mono="$(awk 'BEGIN{getline x < "/proc/uptime"; split(x,a," "); print a[1]}')"
    phase="$(cat "$PHASE_FILE" 2>/dev/null || echo unknown)"
    sensor_text="$(sensors 2>/dev/null)"
    tctl="$(awk '/Tctl/{v=$2; gsub(/[+°C]/,"",v); print v; exit}' <<<"$sensor_text")"
    ccd="$(awk '/Tccd/{v=$2; gsub(/[+°C]/,"",v); if(v+0>m)m=v+0} END{if(m)printf "%.1f",m}' <<<"$sensor_text")"
    nvme="$(awk '/^Composite/{v=$2; gsub(/[+°C]/,"",v); if(v+0>m)m=v+0} END{if(m)printf "%.1f",m}' <<<"$sensor_text")"
    mhz="$(awk '/cpu MHz/{s+=$4;n++} END{printf "%.0f",(n?s/n:0)}' /proc/cpuinfo)"
    printf '%s,%s,%s,%s,%s,%s,%s\n' "$wall" "$mono" "$phase" "$tctl" "$ccd" "$mhz" "$nvme" >> "$HOST_CSV"
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

log "Starting 1 Hz telemetry and ${CONCURRENCY} request workers per GPU"
gpu_logger &
LOGGER_PID=$!
host_logger &
HOST_LOGGER_PID=$!
for _ in $(seq 1 "$CONCURRENCY"); do
  request_worker gpu0 "http://127.0.0.1:${GPU0_PORT}" "$GPU0_PAYLOAD" &
  WORKER_PIDS+=("$!")
  request_worker gpu1 "http://127.0.0.1:${GPU1_PORT}" "$GPU1_PAYLOAD" &
  WORKER_PIDS+=("$!")
done
WORKLOAD_STARTED=1

printf 'warmup\n' > "$PHASE_FILE"
printf '%s,warmup-started\n' "$(date -u +%FT%T.%3NZ)" >> "$EVENTS"
log "Warm-up started (${WARMUP_S}s)"
sleep "$WARMUP_S"

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
awk -v a="$warm0" -v b="$warm1" -v min="$MIN_WARMUP_POWER_W" \
  'BEGIN{exit !((a+0)>=min && (b+0)>=min)}' || {
    echo "Saturation gate failed: both GPUs must average at least ${MIN_WARMUP_POWER_W} W during warm-up" >&2
    exit 1
  }

printf 'measured\n' > "$PHASE_FILE"
printf '%s,measured-started\n' "$(date -u +%FT%T.%3NZ)" >> "$EVENTS"
log "Measured 600 W run started (${DURATION_S}s)"

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
  [[ "$(docker inspect "$GPU0_CONTAINER" --format '{{.State.Running}}' 2>/dev/null || true)" == "true" ]] || {
    echo "GPU0 vLLM container exited" >&2
    exit 1
  }

  current_max_temp="$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | awk 'm<$1{m=$1}END{print m+0}')"
  awk -v t="$current_max_temp" -v limit="$GPU_ABORT_C" 'BEGIN{exit !(t>=limit)}' && {
    echo "Emergency cutoff: GPU temperature reached ${current_max_temp} C (limit ${GPU_ABORT_C} C)" >&2
    exit 1
  }

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

  now="$(date +%s)"
  if ((now >= next_update)); then
    elapsed=$((now - started_epoch))
    snapshot="$(nvidia-smi \
      --query-gpu=index,power.draw.average,temperature.gpu,clocks.current.graphics,utilization.gpu \
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
wait "$LOGGER_PID" "$HOST_LOGGER_PID" 2>/dev/null || true
LOGGER_PID=""
HOST_LOGGER_PID=""

nvidia-smi -q > "$OUT/nvidia-after.txt"
docker logs "$GPU0_CONTAINER" > "$OUT/gpu0-vllm.log" 2>&1 || true

python3 "$(dirname "$0")/summarize-dual-vllm.py" \
  "$GPU_CSV" "$HOST_CSV" "$REQUESTS_CSV" "$SUMMARY_JSON" \
  "$OUT/nvidia-before.txt" "$OUT/nvidia-after.txt"

log "PASS — summary: $SUMMARY_JSON"
cat "$SUMMARY_JSON"
