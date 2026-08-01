#!/usr/bin/env bash
set -uo pipefail

ROOT=/home/michael/bench-deepseek-v4-flash-0731
LOGS="$ROOT/logs"
EXTRACT="$ROOT/tooling/scripts/extract_cost.py"
STATUS=/tmp/bench-autopilot/status.json
SIDELOG=/tmp/bench-autopilot/cost-sidecar.log

while true; do
  generated=0
  while IFS= read -r summary; do
    dir=${summary%/summary.json}
    [[ -f "$dir/workspace_final.tar.gz" ]] || continue
    [[ -f "$dir/cost.json" ]] && continue
    if python3 "$EXTRACT" "$dir" >>"$SIDELOG" 2>&1; then
      printf '%s generated %s/cost.json\n' "$(date -u +%FT%TZ)" "$dir" >>"$SIDELOG"
      generated=$((generated + 1))
    else
      printf '%s extract failed for %s\n' "$(date -u +%FT%TZ)" "$dir" >>"$SIDELOG"
    fi
  done < <(find "$LOGS" -mindepth 2 -maxdepth 2 -type f -name summary.json \
           -path '*deepseek-v4-flash-0731*' | sort)

  phase=$(python3 -c "import json; print(json.load(open('$STATUS')).get('phase',''))" 2>/dev/null || true)
  summaries=$(find "$LOGS" -mindepth 2 -maxdepth 2 -type f -name summary.json \
              -path '*p*_deepseek-v4-flash-0731_v*' | wc -l)
  costs=$(find "$LOGS" -mindepth 2 -maxdepth 2 -type f -name cost.json \
          -path '*p*_deepseek-v4-flash-0731_v*' | wc -l)
  printf '%s phase=%s summaries=%s costs=%s generated=%s\n' \
    "$(date -u +%FT%TZ)" "$phase" "$summaries" "$costs" "$generated" >>"$SIDELOG"

  if [[ "$phase" == COMPLETE && "$summaries" -eq 36 && "$costs" -eq 36 ]]; then
    exit 0
  fi
  sleep 60
done
