#!/usr/bin/env bash
# Six-seed host-crossover campaign runner (PREREGISTRATION.md section 3).
#
#   seeds 101/211/307 (phase_a): Tower1 serves Qwen3.8, Tower3 serves Qwen3.6
#   seeds 401/503/601 (phase_b): the exact model artifacts swap hosts
#
# Task order is interleaved, family-major, with alternating model start:
# for seed index s and family index f, the model launched FIRST is q38 when
# (s + f) is even, q36 when odd; the second model launches STAGGER_SECS later
# and both run concurrently (one per tower) to keep time-of-day matched.
# This rule is deterministic and fixed before any cell runs.
#
# Per phase, before any clean cell starts, this script verifies MECHANICALLY:
#   1. 500 W power cap on every GPU of both towers (nvidia-smi query);
#   2. each tunnel port serves EXACTLY the expected model alias for the phase;
#   3. Tower1 ODS drain: refuse to start if the second llama-server
#      (config drain.forbidden_containers, i.e. ods-llama-server) is running.
# The full preflight evidence is written to logs/corrective/preflight-*.json.
#
# Infra failures inside a cell are quarantined + same-seed rerun and ledgered
# by cell_supervisor.py (logs/corrective/rerun_ledger.jsonl). An exhausted
# cell (still infra after MAX_INFRA_RETRIES) aborts the campaign: stop and
# report, never improvise.
#
# Usage:
#   bash tooling/corrective/run_crossover.sh --config tooling/corrective/configs/official-nothink.json \
#        [--seeds 101,211,307] [--dry-run] [--max-infra-retries 3]
#
# --dry-run parses the config, prints the full cell plan, and RUNS the
# preflight checks (read-only), reporting pass/fail without starting cells.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLING="$(cd "$HERE/.." && pwd)"
REPO_ROOT="$(cd "$TOOLING/.." && pwd)"
CORR_LOGS="$REPO_ROOT/logs/corrective"
STAGGER_SECS="${BENCH_CROSSOVER_STAGGER_SECS:-30}"

CONFIG=""
SEEDS_CSV=""
DRY_RUN=0
MAX_INFRA_RETRIES=3

while [ $# -gt 0 ]; do
  case "$1" in
    --config) CONFIG="$2"; shift 2 ;;
    --seeds) SEEDS_CSV="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --max-infra-retries) MAX_INFRA_RETRIES="$2"; shift 2 ;;
    -h|--help) grep "^#" "$0" | sed "s/^# \{0,1\}//"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -n "$CONFIG" ] || { echo "ERROR: --config is required" >&2; exit 2; }
[ -f "$CONFIG" ] || { echo "ERROR: config not found: $CONFIG" >&2; exit 2; }

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
die() { log "ERROR: $*" >&2; exit 1; }

cfg_get() { python3 -c '
import json, sys
cfg = json.load(open(sys.argv[1]))
cur = cfg
for k in sys.argv[2].split("."):
    cur = cur[int(k)] if isinstance(cur, list) else cur[k]
if isinstance(cur, (list, tuple)):
    print(" ".join(str(x) for x in cur))
else:
    print(cur)
' "$CONFIG" "$1"; }

ARM="$(cfg_get arm)"
FAMILIES=($(cfg_get families))
ALL_SEEDS=($(cfg_get seeds))
POWER_CAP_W="$(cfg_get power_cap_w)"
DRAIN_TOWER="$(cfg_get drain.tower)"
FORBIDDEN=($(cfg_get drain.forbidden_containers))

if [ -n "$SEEDS_CSV" ]; then
  SEEDS=(${SEEDS_CSV//,/ })
  for s in "${SEEDS[@]}"; do
    ok=0; for a in "${ALL_SEEDS[@]}"; do [ "$s" = "$a" ] && ok=1; done
    [ "$ok" = "1" ] || die "seed $s is not in arm $ARM (fixed-N design: no extra seeds)"
  done
else
  SEEDS=("${ALL_SEEDS[@]}")
fi

phase_of_seed() { python3 -c '
import json, sys
cfg = json.load(open(sys.argv[1])); seed = int(sys.argv[2])
for phase, plan in cfg["host_plan"].items():
    if seed in plan["seeds"]:
        print(phase); raise SystemExit(0)
raise SystemExit(1)
' "$CONFIG" "$1"; }

plan_field() { # phase model_key field
  cfg_get "host_plan.$1.$2.$3"
}
model_alias() { cfg_get "models.$1.alias"; }

# ---------- preflight ----------------------------------------------------

preflight_phase() {
  local phase="$1" fail=0
  local record="$CORR_LOGS/preflight-$ARM-$phase-$(date -u +%Y%m%dT%H%M%SZ).json"
  mkdir -p "$CORR_LOGS"
  local results=()

  for mk in q38 q36; do
    local tower port alias
    tower="$(plan_field "$phase" "$mk" tower)"
    port="$(plan_field "$phase" "$mk" port)"
    alias="$(model_alias "$mk")"

    # 1. power cap on every GPU of the tower
    local caps cap_ok=1
    caps="$(ssh -o BatchMode=yes -o ConnectTimeout=10 "$tower" \
      "nvidia-smi --query-gpu=power.limit --format=csv,noheader,nounits" 2>&1)" || cap_ok=0
    if [ "$cap_ok" = "1" ]; then
      while IFS= read -r line; do
        awk -v c="$line" -v want="$POWER_CAP_W" \
          'BEGIN { exit (c+0 == want+0) ? 0 : 1 }' || cap_ok=0
      done <<< "$caps"
    fi
    [ "$cap_ok" = "1" ] || fail=1
    results+=("{\"check\":\"power_cap\",\"tower\":\"$tower\",\"want_w\":$POWER_CAP_W,\"got\":\"${caps//$'\n'/,}\",\"pass\":$( [ $cap_ok = 1 ] && echo true || echo false )}")
    log "preflight[$phase] power cap $tower: $( [ $cap_ok = 1 ] && echo PASS || echo FAIL ) ($caps W, want $POWER_CAP_W W)"

    # 2. endpoint serves exactly the expected alias for this phase
    local ep_ok=1 served
    served="$(curl -sf --max-time 8 "http://127.0.0.1:${port}/v1/models" \
      | python3 -c 'import json,sys; d=json.load(sys.stdin); print(",".join(str(x.get("id")) for x in d.get("data",[])))' 2>/dev/null)" || ep_ok=0
    if [ "$ep_ok" = "1" ]; then
      [ "$served" = "$alias" ] || ep_ok=0
    fi
    [ "$ep_ok" = "1" ] || fail=1
    results+=("{\"check\":\"endpoint_alias\",\"tower\":\"$tower\",\"port\":$port,\"want\":\"$alias\",\"got\":\"${served:-DOWN}\",\"pass\":$( [ $ep_ok = 1 ] && echo true || echo false )}")
    log "preflight[$phase] endpoint :$port -> ${served:-DOWN} (want $alias): $( [ $ep_ok = 1 ] && echo PASS || echo FAIL )"
  done

  # 3. ODS drain on the drain tower: the second llama-server must be DOWN
  local drain_ok=1 names
  names="$(ssh -o BatchMode=yes -o ConnectTimeout=10 "$DRAIN_TOWER" \
    'docker ps --format "{{.Names}}"' 2>&1)" || drain_ok=0
  if [ "$drain_ok" = "1" ]; then
    for c in "${FORBIDDEN[@]}"; do
      if grep -Fxq "$c" <<< "$names"; then drain_ok=0; fi
    done
  fi
  [ "$drain_ok" = "1" ] || fail=1
  results+=("{\"check\":\"ods_drain\",\"tower\":\"$DRAIN_TOWER\",\"forbidden\":\"${FORBIDDEN[*]}\",\"running\":\"${names//$'\n'/,}\",\"pass\":$( [ $drain_ok = 1 ] && echo true || echo false )}")
  log "preflight[$phase] ODS drain on $DRAIN_TOWER: $( [ $drain_ok = 1 ] && echo PASS || echo "FAIL (a forbidden inference container is running)" )"

  {
    echo "{\"arm\":\"$ARM\",\"phase\":\"$phase\",\"t\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"stagger_secs\":$STAGGER_SECS,"
    echo "\"interleave_rule\":\"first model = q38 if (seed_index + family_index) even else q36\","
    echo "\"pass\":$( [ $fail = 0 ] && echo true || echo false ),\"checks\":["
    local IFS=,; echo "${results[*]}"
    echo "]}"
  } > "$record"
  log "preflight[$phase] record -> $record"
  return $fail
}

# ---------- plan + execution ---------------------------------------------

log "arm=$ARM seeds=${SEEDS[*]} families=${#FAMILIES[@]} dry_run=$DRY_RUN"

declare -A PREFLIGHTED
seed_index=-1
for seed in "${SEEDS[@]}"; do
  seed_index=$((seed_index + 1))
  phase="$(phase_of_seed "$seed")" || die "seed $seed not in host_plan"

  if [ -z "${PREFLIGHTED[$phase]:-}" ]; then
    if preflight_phase "$phase"; then
      PREFLIGHTED[$phase]=pass
    else
      PREFLIGHTED[$phase]=fail
      if [ "$DRY_RUN" = "1" ]; then
        log "preflight[$phase] FAILED (dry-run: continuing to print the plan)"
      else
        die "preflight failed for phase $phase — refusing to start clean runs"
      fi
    fi
  fi

  fam_index=-1
  for family in "${FAMILIES[@]}"; do
    fam_index=$((fam_index + 1))
    if [ $(( (seed_index + fam_index) % 2 )) -eq 0 ]; then
      first=q38; second=q36
    else
      first=q36; second=q38
    fi

    if [ "$DRY_RUN" = "1" ]; then
      python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$first" \
        --family "$family" --seed "$seed" --dry-run
      python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$second" \
        --family "$family" --seed "$seed" --dry-run
      continue
    fi

    log "seed $seed family $family: start order $first -> $second (stagger ${STAGGER_SECS}s)"
    python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$first" \
      --family "$family" --seed "$seed" --max-infra-retries "$MAX_INFRA_RETRIES" &
    pid_first=$!
    sleep "$STAGGER_SECS"
    python3 "$HERE/cell_supervisor.py" --config "$CONFIG" --model-key "$second" \
      --family "$family" --seed "$seed" --max-infra-retries "$MAX_INFRA_RETRIES" &
    pid_second=$!

    rc_first=0; rc_second=0
    wait "$pid_first" || rc_first=$?
    wait "$pid_second" || rc_second=$?
    if [ "$rc_first" != "0" ] || [ "$rc_second" != "0" ]; then
      die "cell supervisor failed (rc $first=$rc_first $second=$rc_second) at seed $seed family $family — stop and report (see $CORR_LOGS/rerun_ledger.jsonl)"
    fi
  done
done

if [ "$DRY_RUN" = "1" ]; then
  log "dry-run complete: plan printed above; preflight results: $(for k in "${!PREFLIGHTED[@]}"; do printf '%s=%s ' "$k" "${PREFLIGHTED[$k]}"; done)"
else
  log "crossover complete for arm=$ARM seeds=${SEEDS[*]}"
  log "next: python3 $HERE/evidence_manifest.py build --config $CONFIG --out $CORR_LOGS/manifest-$ARM.jsonl"
fi
