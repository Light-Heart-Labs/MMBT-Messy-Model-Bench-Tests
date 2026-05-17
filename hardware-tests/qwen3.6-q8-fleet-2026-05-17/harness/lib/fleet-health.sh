#!/usr/bin/env bash
# fleet-health.sh — per-host liveness/idle check. Emits one line per host:
#   HOST  bench-host=ALIVE|DEAD  cell=<basename>  last-write=Nm
#
# Use this every cron firing to catch silently-dead bench-hosts like the
# M5 27B SSH-disconnect bug.
#
# Usage: fleet-health.sh [stale_min]   (default 10 min)

set -u
STALE_MIN="${1:-10}"

probe() {
    local name="$1" how="$2"
    # ONE remote command that emits four labeled lines, easy to parse
    local cmd='
        bh=$(pgrep -fa bench-host.sh 2>/dev/null | grep -v "fleet-health\|/bin/bash -c" | head -1)
        cell=$(ls -td /tmp/bench-fleet-out-*-*-*/ctx*conc*/ 2>/dev/null | head -1)
        mtime=0
        [[ -n "$cell" && -f "$cell/bench-cell.log" ]] && mtime=$(stat -c %Y "$cell/bench-cell.log" 2>/dev/null || stat -f %m "$cell/bench-cell.log" 2>/dev/null)
        [[ -z "$mtime" || "$mtime" = "0" ]] && [[ -n "$cell" && -f "$cell/power.csv" ]] && mtime=$(stat -c %Y "$cell/power.csv" 2>/dev/null || stat -f %m "$cell/power.csv" 2>/dev/null)
        echo "BH=${bh:-NONE}"
        echo "CELL=${cell:-NONE}"
        echo "MTIME=${mtime:-0}"
        echo "NOW=$(date +%s)"
    '
    local out
    if [[ "$how" == "local" ]]; then
        out=$(bash -c "$cmd" 2>/dev/null)
    else
        out=$(ssh -o ConnectTimeout=10 "$how" "$cmd" 2>/dev/null)
    fi

    local bh=$(echo "$out" | grep ^BH= | head -1 | cut -d= -f2-)
    local cell=$(echo "$out" | grep ^CELL= | head -1 | cut -d= -f2-)
    local mtime=$(echo "$out" | grep ^MTIME= | head -1 | cut -d= -f2-)
    local now=$(echo "$out" | grep ^NOW= | head -1 | cut -d= -f2-)
    [[ -z "$now" ]] && now=$(date +%s)
    [[ -z "$mtime" ]] && mtime=0

    local bh_state="ALIVE"
    [[ "$bh" == "NONE" ]] && bh_state="DEAD"

    local cell_short="-"
    [[ "$cell" != "NONE" ]] && cell_short=$(basename "$cell")

    local age_min=$(( (now - mtime) / 60 ))
    (( mtime == 0 )) && age_min="-"

    local stale=""
    if [[ "$age_min" != "-" ]] && (( age_min > STALE_MIN )); then
        stale="  ⚠️ STALE"
    fi

    printf "%-11s  bench-host=%-5s  cell=%-30s  last-write=%sm%s\n" "$name" "$bh_state" "$cell_short" "$age_min" "$stale"
}

probe tower2     local
probe strix-halo strix-halo
probe spark      spark
probe m5-mbp     m5-mbp
