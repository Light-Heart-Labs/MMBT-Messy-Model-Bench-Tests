#!/usr/bin/env bash
set -uo pipefail

ROOT=/home/michael/bench-gemma4-31b-q4
LOGS="$ROOT/logs"
DEPLOY="$ROOT/tooling/deployments/gemma4-31b-q4-tower2"
CSV=/home/michael/gemma4-campaign-state/telemetry/gemma4-31b-q4-gpu.csv
REPORT=/home/michael/gemma4-campaign-state/telemetry/gemma4-31b-q4-report.json
SIDELOG=/home/michael/gemma4-campaign-state/telemetry/sidecar.log

while true; do
  if [[ -s "$CSV" ]]; then
    python3 "$DEPLOY/analyze_replica_telemetry.py" \
      --csv "$CSV" --logs-dir "$LOGS" --cap-per-gpu 500 \
      --write-run-artifacts --output "$REPORT" >>"$SIDELOG" 2>&1 || true
  fi

  while IFS= read -r summary; do
    run_dir=${summary%/summary.json}
    [[ -f "$run_dir/workspace_final.tar.gz" ]] || continue
    [[ -f "$run_dir/cost.json" ]] && continue
    python3 "$ROOT/tooling/scripts/extract_cost.py" "$run_dir" >>"$SIDELOG" 2>&1 || true
  done < <(find "$LOGS" -mindepth 2 -maxdepth 2 -type f -name summary.json \
           -path '*gemma4-31b-q4*' | sort)

  sleep 60
done
