#!/usr/bin/env bash
set -euo pipefail

CONFIG=/home/michael/.openclaw/openclaw.json
STATE_DIR=/home/michael/gemma4-campaign-state
BACKUP=$STATE_DIR/openclaw.gemma-single-provider.json
MODEL=Gemma-4-31B-it-QAT-Q4_0
OPENCLAW=/home/michael/.npm-global/bin/openclaw

install -d -m 700 "$STATE_DIR"
if [[ ! -e "$BACKUP" ]]; then
  install -m 600 "$CONFIG" "$BACKUP"
fi

patch_file="$(mktemp "$STATE_DIR/openclaw-dual-replica-patch.XXXXXX.json")"
dry_run_file="$(mktemp "$STATE_DIR/openclaw-dual-replica-dry-run.XXXXXX.json")"
chmod 0600 "$patch_file" "$dry_run_file"
cleanup() {
  rm -f -- "$patch_file" "$dry_run_file"
}
trap cleanup EXIT

jq --arg model "$MODEL" '
  {
    models: {
      providers: {
        tower1: (.models.providers.tower | .baseUrl = "http://127.0.0.1:8001/v1")
      }
    },
    agents: {
      defaults: {
        models: {
          ("tower1/" + $model): {alias: "Pixel"}
        }
      },
      list: (
        .agents.list
        | map(
            if .id == "main" then
              . + {model: {primary: ("tower/" + $model)}}
            elif .id == "pixel" then
              . + {model: {primary: ("tower1/" + $model)}}
            else
              .
            end
          )
      )
    }
  }
' "$CONFIG" >"$patch_file"

"$OPENCLAW" config patch --file "$patch_file" --dry-run --json >"$dry_run_file"
jq -e '.ok == true' "$dry_run_file" >/dev/null
"$OPENCLAW" config patch --file "$patch_file" >/dev/null
"$OPENCLAW" config validate --json | jq -e '.valid == true'

jq -r --arg model "$MODEL" '
  [
    .models.providers.tower.baseUrl,
    .models.providers.tower1.baseUrl,
    (.agents.list[] | select(.id == "main") | .model.primary),
    (.agents.list[] | select(.id == "pixel") | .model.primary)
  ] | @tsv
' "$CONFIG"
sha256sum "$BACKUP" "$CONFIG"
