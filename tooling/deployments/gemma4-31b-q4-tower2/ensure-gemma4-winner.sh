#!/usr/bin/env bash
# Recover the preregistered two-replica Gemma winner and prove both API lanes.
set -euo pipefail

SERVICES=(
  mmbt-gemma4@replica-gpu0-q8-s4.service
  mmbt-gemma4@replica-gpu1-q8-s4.service
)
PORTS=(8000 8001)
GRACE_SECS="${GEMMA_RECOVERY_GRACE_SECS:-300}"

for service in "${SERVICES[@]}"; do
  systemctl --user start "$service"
done

deadline=$(( $(date +%s) + GRACE_SECS ))
while (( $(date +%s) < deadline )); do
  ready=1
  for i in "${!SERVICES[@]}"; do
    if ! systemctl --user is-active --quiet "${SERVICES[$i]}" || \
       ! curl -fsS --max-time 5 "http://127.0.0.1:${PORTS[$i]}/v1/models" >/dev/null; then
      ready=0
    fi
  done
  if (( ready )); then
    printf 'Gemma winner healthy: %s\n' "${PORTS[*]}"
    exit 0
  fi
  sleep 5
done

for i in "${!SERVICES[@]}"; do
  printf '%s active=%s endpoint=%s\n' \
    "${SERVICES[$i]}" \
    "$(systemctl --user is-active "${SERVICES[$i]}" 2>/dev/null || true)" \
    "$(curl -fsS --max-time 5 "http://127.0.0.1:${PORTS[$i]}/v1/models" >/dev/null && echo up || echo down)" >&2
done
exit 1
