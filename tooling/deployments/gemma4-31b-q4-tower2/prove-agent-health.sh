#!/usr/bin/env bash
set -euo pipefail

PHASE="${1:-}"
OUT_ROOT="${2:-/home/michael/gemma4-campaign-state/health}"
if [[ -z "$PHASE" ]]; then
  printf 'Usage: %s PHASE [OUTPUT_ROOT]\n' "$0" >&2
  exit 64
fi

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
out_dir="$OUT_ROOT/$PHASE-$timestamp"
install -d -m 700 "$out_dir"
health_max_tokens="${HEALTH_MAX_TOKENS:-262144}"
health_timeout_seconds="${HEALTH_TIMEOUT_SECONDS:-180}"

probe() {
  local agent="$1"
  local portal_container="$2"
  local requested_model="$3"
  local marker="MMBT_${PHASE}_${agent}_${timestamp}"
  local api_key response http_code body_file summary_file

  api_key="$(docker inspect "$portal_container" | jq -r '.[0].Config.Env[]' | sed -n 's/^OPENAI_API_KEY=//p' | head -n 1)"
  if [[ -z "$api_key" ]]; then
    printf 'No portal API key found for %s\n' "$portal_container" >&2
    return 1
  fi

  body_file="$out_dir/${agent}.response.json"
  summary_file="$out_dir/${agent}.summary.json"
  response="$(curl --silent --show-error --max-time "$health_timeout_seconds" \
    --write-out $'\n%{http_code}' \
    --config <(printf 'header = "Authorization: Bearer %s"\nheader = "Content-Type: application/json"\n' "$api_key") \
    --data "$(jq -cn --arg model "$requested_model" --arg marker "$marker" --argjson max_tokens "$health_max_tokens" \
      '{model:$model,user:$marker,messages:[{role:"user",content:("Health check. Reply with exactly this marker and nothing else: " + $marker)}],temperature:0,max_tokens:$max_tokens,stream:false}')" \
    http://127.0.0.1:18789/v1/chat/completions)"
  http_code="${response##*$'\n'}"
  printf '%s' "${response%$'\n'*}" >"$body_file"

  jq -n \
    --arg phase "$PHASE" \
    --arg timestamp "$timestamp" \
    --arg agent "$agent" \
    --arg portal "$portal_container" \
    --arg requested_model "$requested_model" \
    --argjson max_tokens "$health_max_tokens" \
    --arg marker "$marker" \
    --arg http_code "$http_code" \
    --arg response_id "$(jq -r '.id // ""' "$body_file")" \
    --arg finish_reason "$(jq -r '.choices[0].finish_reason // ""' "$body_file")" \
    --arg content "$(jq -r '.choices[0].message.content // ""' "$body_file")" \
    --arg error "$(jq -r '.error.message // .detail // ""' "$body_file")" \
    --arg raw_sha256 "$(sha256sum "$body_file" | cut -d' ' -f1)" \
    '{phase:$phase,timestamp:$timestamp,agent:$agent,portal:$portal,requested_model:$requested_model,max_tokens:$max_tokens,http_code:($http_code|tonumber),response_id:$response_id,finish_reason:$finish_reason,content:$content,error:$error,raw_sha256:$raw_sha256,passed:(($http_code=="200") and ($content|contains($marker)) and ($error==""))}' \
    >"$summary_file"

  jq -c . "$summary_file"
  jq -e '.passed == true' "$summary_file" >/dev/null
}

probe sanctuary sanctuary-portal openclaw
probe pixel pixel-portal openclaw/pixel

find "$out_dir" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum >"$out_dir/SHA256SUMS"
printf '%s\n' "$out_dir"
