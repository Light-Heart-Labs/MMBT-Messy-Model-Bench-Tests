#!/usr/bin/env bash
set -euo pipefail

UNIT_SOURCE=/home/michael/bench-gemma4-31b-q4/tooling/deployments/gemma4-31b-q4-tower2/mmbt-gemma4@.service
UNIT_NAME=mmbt-gemma4@.service
KNOWN_INSTANCES=(
  single-gpu0 single-gpu1 dual-layer-1to1 dual-row-1to1
  replica-gpu0 replica-gpu1
  replica-gpu0-f16-s2 replica-gpu1-f16-s2
  replica-gpu0-q8-s4 replica-gpu1-q8-s4
  replica-gpu0-q8-s6 replica-gpu1-q8-s6
)

usage() {
  printf 'Usage: %s install|start <single-gpu0|single-gpu1|dual-layer-1to1|dual-row-1to1|dual-independent-replicas>|stop|status\n' "$0" >&2
  exit 64
}

install_unit() {
  test -r "$UNIT_SOURCE"
  systemctl --user link "$UNIT_SOURCE" >/dev/null
  systemctl --user daemon-reload
}

stop_all() {
  local instance
  for instance in "${KNOWN_INSTANCES[@]}"; do
    systemctl --user stop "mmbt-gemma4@${instance}.service" 2>/dev/null || true
  done
}

deepseek_is_running() {
  [[ "$(docker inspect -f '{{.State.Running}}' deepseek-v4-flash-0731 2>/dev/null || true)" == true ]]
}

start_candidate() {
  local candidate="$1"
  if deepseek_is_running; then
    printf 'Refusing to start Gemma while deepseek-v4-flash-0731 owns the GPUs.\n' >&2
    exit 69
  fi
  install_unit
  stop_all
  case "$candidate" in
    single-gpu0|single-gpu1|dual-layer-1to1|dual-row-1to1)
      systemctl --user start "mmbt-gemma4@${candidate}.service"
      ;;
    dual-independent-replicas)
      systemctl --user start mmbt-gemma4@replica-gpu0.service mmbt-gemma4@replica-gpu1.service
      ;;
    *) usage ;;
  esac
}

show_status() {
  systemctl --user --no-pager --full list-units 'mmbt-gemma4@*.service'
  nvidia-smi --query-gpu=index,power.limit,memory.total,memory.used,utilization.gpu,power.draw,temperature.gpu \
    --format=csv,noheader,nounits
}

case "${1:-}" in
  install) install_unit ;;
  start) [[ $# -eq 2 ]] || usage; start_candidate "$2" ;;
  stop) stop_all ;;
  status) show_status ;;
  *) usage ;;
esac
