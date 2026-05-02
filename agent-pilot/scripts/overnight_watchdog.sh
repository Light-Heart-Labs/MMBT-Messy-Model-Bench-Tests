#!/usr/bin/env bash
# Overnight watchdog for the 2026-05-02 bench chain triple.
#
# Responsibilities:
# 1. Snapshot progress every 5 min to /tmp/chain_progress.log
# 2. Health-check vllm-qwen36-awq (auto-restart if dead). vllm-coder-next is
#    the dream-expo demo container — log-only, never auto-restart.
# 3. Hourly local commit of agent-pilot/logs/ artifacts (preserves work
#    against power loss).
# 4. When all 3 chain orchestrators have exited:
#    a. Scan for finish_reason=api_error runs (vLLM blip casualties),
#       delete their summary.json + workspace_final.tar.gz so the make-up
#       pass picks them up.
#    b. Re-run all 3 chain scripts (skip-if-summary-and-tarball-exist logic
#       only re-runs missing or just-cleaned entries).
#    c. Final commit + push to origin master.
#    d. Print summary to stdout (becomes the notification when the
#       run_in_background task ends).
#
# State files:
#   /tmp/chain_watchdog.log    — watchdog-internal events
#   /tmp/chain_progress.log    — 5-min progress snapshots
#   /tmp/chain_pids.txt        — chain orchestrator PIDs (3 lines, space-sep)
#
# Usage: bash overnight_watchdog.sh   (designed to run via Bash run_in_background)

set -u

CHAIN_PIDS_FILE=/tmp/chain_pids.txt
PROGRESS_LOG=/tmp/chain_progress.log
WATCHDOG_LOG=/tmp/chain_watchdog.log
LOOP_INTERVAL=300        # 5 min
COMMIT_INTERVAL=3600     # 1 hr
VLLM_RESTART_TIMEOUT=240 # 4 min wait for re-launched vLLM

# Read chain PIDs
read -r -a CHAIN_PIDS < $CHAIN_PIDS_FILE

LAST_COMMIT_TS=$(date +%s)

log() {
  printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$WATCHDOG_LOG"
}

# Expected run names per chain
phaseb_27b_runs() {
  for v in 7 8 9 10; do echo p3_doc_27b_v$v; done
  for v in 4 5 6 7 8 9 10; do echo p3_market_27b_v$v; done
}
phaseb_coder_runs() {
  for v in 9 10; do echo p2_hallucination_coder_v$v; done
  for cell in business doc market; do
    for v in 4 5 6 7 8 9 10; do echo p3_${cell}_coder_v$v; done
  done
}
nothink_runs() {
  for cell in p1_bugfix p1_refactor p1_testwrite p2_ci p2_extract p2_hallucination p2_triage p3_business p3_doc p3_market p3_pm p3_writing; do
    for v in 1 2 3 4 5 6 7 8 9 10; do echo ${cell}_27b-nothink_v$v; done
  done
}

count_done() {
  # $1 = function emitting expected run names
  local fn=$1 cnt=0 n
  while read -r n; do
    [ -f ~/bench/agent-pilot/logs/$n/summary.json ] && cnt=$((cnt+1))
  done < <($fn)
  echo $cnt
}

snapshot_progress() {
  local now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local p27=$(count_done phaseb_27b_runs)
  local pcd=$(count_done phaseb_coder_runs)
  local pnt=$(count_done nothink_runs)
  local active=$(docker ps --filter name=bench-sandbox --format '{{.Names}}' | wc -l)
  local g0=$(nvidia-smi --query-gpu=memory.used,utilization.gpu,power.draw --format=csv,noheader -i 0 | tr -s ' ')
  local g1=$(nvidia-smi --query-gpu=memory.used,utilization.gpu,power.draw --format=csv,noheader -i 1 | tr -s ' ')
  printf '[%s] 27B-PhaseB:%d/11  Coder-PhaseB:%d/23  27B-nothink:%d/120  active_sandboxes:%d  GPU0=[%s]  GPU1=[%s]\n' \
    "$now" "$p27" "$pcd" "$pnt" "$active" "$g0" "$g1" >> "$PROGRESS_LOG"
}

vllm_qwen36_launch() {
  docker run -d \
    --name vllm-qwen36-awq \
    --gpus '"device=0"' \
    --shm-size 8g \
    -v /home/michael/models:/models:ro \
    -p 127.0.0.1:8002:8000 \
    vllm/vllm-openai:latest \
    --model /models/cyankiwi-Qwen3.6-27B-AWQ-INT4 \
    --served-model-name qwen3.6-27b-awq \
    --host 0.0.0.0 --port 8000 \
    --tensor-parallel-size 1 \
    --max-model-len 262144 \
    --gpu-memory-utilization 0.92 \
    --reasoning-parser qwen3 \
    --enable-auto-tool-choice \
    --tool-call-parser qwen3_xml >> "$WATCHDOG_LOG" 2>&1
}

cleanup_zombie_sandboxes() {
  # Remove bench-sandbox-* containers whose corresponding run has completed
  # (summary.json + workspace_final.tar.gz both exist). Sandboxes run
  # `sleep infinity` after the harness exits and accumulate otherwise.
  local cleaned=0 c name
  while read -r c; do
    name=${c#bench-sandbox-}
    if [ -f ~/bench/agent-pilot/logs/$name/summary.json ] && \
       [ -f ~/bench/agent-pilot/logs/$name/workspace_final.tar.gz ]; then
      docker rm -f "$c" >/dev/null 2>&1 && cleaned=$((cleaned+1))
    fi
  done < <(docker ps --filter name=bench-sandbox --format '{{.Names}}')
  if (( cleaned > 0 )); then
    log "cleaned $cleaned zombie sandboxes"
  fi
}

vllm_health_check() {
  if curl -sf -m 5 http://127.0.0.1:8002/v1/models >/dev/null 2>&1; then
    : # healthy
  else
    log "WARN: vllm-qwen36-awq port 8002 unreachable; checking container state"
    if docker ps --filter name=vllm-qwen36-awq --format '{{.Status}}' | grep -q '^Up'; then
      log "WARN: container is up but endpoint not reachable; not restarting (might be transient)"
    else
      log "ERROR: vllm-qwen36-awq is DOWN; rebuilding container"
      docker rm -f vllm-qwen36-awq >/dev/null 2>&1
      vllm_qwen36_launch
      log "vllm-qwen36-awq launch issued; waiting up to ${VLLM_RESTART_TIMEOUT}s for ready"
      local waited=0
      while (( waited < VLLM_RESTART_TIMEOUT )); do
        if curl -sf -m 5 http://127.0.0.1:8002/v1/models >/dev/null 2>&1; then
          log "vllm-qwen36-awq ready after ${waited}s"
          return 0
        fi
        sleep 10; waited=$((waited+10))
      done
      log "ERROR: vllm-qwen36-awq did not become ready within ${VLLM_RESTART_TIMEOUT}s"
    fi
  fi

  if ! curl -sf -m 5 http://127.0.0.1:8000/v1/models >/dev/null 2>&1; then
    log "WARN: vllm-coder-next port 8000 unreachable (dream-expo container; not auto-restarting)"
  fi
}

hourly_commit() {
  local now=$(date +%s)
  if (( now - LAST_COMMIT_TS < COMMIT_INTERVAL )); then return; fi
  LAST_COMMIT_TS=$now

  cd ~/bench || { log "ERROR: cd ~/bench failed in hourly_commit"; return; }
  git add agent-pilot/logs/ 2>>"$WATCHDOG_LOG"
  if git diff --cached --quiet 2>/dev/null; then
    log "hourly commit: no changes"
    return
  fi
  local p27=$(count_done phaseb_27b_runs)
  local pcd=$(count_done phaseb_coder_runs)
  local pnt=$(count_done nothink_runs)
  local stamp=$(date -u +%Y-%m-%dT%H:%MZ)
  local msg="Bench logs snapshot $stamp [27B-PhaseB:$p27/11 Coder-PhaseB:$pcd/23 27B-nothink:$pnt/120]"
  if git commit -m "$msg" >>"$WATCHDOG_LOG" 2>&1; then
    log "hourly commit: $msg"
    # Push the new commit to origin so partial progress survives a host crash
    local cur_branch=$(git rev-parse --abbrev-ref HEAD)
    if git push origin "HEAD:$cur_branch" >>"$WATCHDOG_LOG" 2>&1; then
      log "pushed hourly commit to origin $cur_branch"
    else
      log "WARN: hourly push to origin $cur_branch failed (will retry next hour)"
    fi
  else
    log "ERROR: hourly commit failed"
  fi
}

clean_api_error_runs() {
  # Delete summary.json + tarball for any run whose finish_reason indicates a
  # transient infra failure that should be retried. Keeps task-honest stuck/done.
  local n cleaned=0
  while read -r n; do
    local sjson=~/bench/agent-pilot/logs/$n/summary.json
    [ -f "$sjson" ] || continue
    local fr=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('finish_reason') or '')" "$sjson" 2>/dev/null)
    case "$fr" in
      api_error:*|"")
        log "make-up: cleaning $n (finish_reason=$fr) for retry"
        rm -f "$sjson" ~/bench/agent-pilot/logs/$n/workspace_final.tar.gz
        cleaned=$((cleaned+1))
        ;;
    esac
  done < <( { phaseb_27b_runs; phaseb_coder_runs; nothink_runs; } )
  log "make-up: cleaned $cleaned api_error runs for retry"
}

end_of_night() {
  log "all 3 chain orchestrators exited; entering end-of-night phase"

  # 1. Final progress snapshot before make-up
  snapshot_progress
  cd ~/bench || { log "ERROR: cd ~/bench failed in end_of_night"; return; }

  # 2. Pre-make-up commit so we capture state before any retry overwrites
  git add agent-pilot/logs/ 2>>"$WATCHDOG_LOG"
  if ! git diff --cached --quiet 2>/dev/null; then
    git commit -m "Bench logs pre-makeup snapshot $(date -u +%Y-%m-%dT%H:%MZ)" >>"$WATCHDOG_LOG" 2>&1
    log "pre-makeup commit complete"
  fi

  # 3. Clean api_error runs for retry
  clean_api_error_runs

  # 4. Re-run all 3 chains (skip-if-done logic limits to missing+cleaned)
  log "make-up: re-running all 3 chains"
  bash agent-pilot/scripts/run_diff_cells_per_model.sh 27b >> /tmp/chain_27b_phaseB.log 2>&1 &
  local M1=$!
  bash agent-pilot/scripts/run_diff_cells_per_model.sh coder >> /tmp/chain_coder_phaseB.log 2>&1 &
  local M2=$!
  bash agent-pilot/scripts/run_full_grid_27b_nothink.sh >> /tmp/chain_27b_nothink_grid.log 2>&1 &
  local M3=$!
  wait $M1 $M2 $M3
  log "make-up passes complete"

  # 5. Final commit
  git add agent-pilot/logs/ 2>>"$WATCHDOG_LOG"
  if ! git diff --cached --quiet 2>/dev/null; then
    local p27=$(count_done phaseb_27b_runs)
    local pcd=$(count_done phaseb_coder_runs)
    local pnt=$(count_done nothink_runs)
    git commit -m "Bench logs final post-makeup $(date -u +%Y-%m-%dT%H:%MZ) [27B-PhaseB:$p27/11 Coder-PhaseB:$pcd/23 27B-nothink:$pnt/120]" >>"$WATCHDOG_LOG" 2>&1
    log "final commit complete"
  fi

  # 6. Push current branch's HEAD (whatever submit/* branch is checked out)
  local cur_branch=$(git rev-parse --abbrev-ref HEAD)
  if git push origin "HEAD:$cur_branch" >>"$WATCHDOG_LOG" 2>&1; then
    log "pushed HEAD to origin $cur_branch"
  else
    log "ERROR: push to origin $cur_branch FAILED — manual fix needed"
  fi

  # 7. Summary to stdout (becomes the run_in_background final notification)
  echo "=== ALL CHAINS COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  echo ""
  echo "27B Phase B:    $(count_done phaseb_27b_runs)/11"
  echo "Coder Phase B:  $(count_done phaseb_coder_runs)/23"
  echo "27B no-think:   $(count_done nothink_runs)/120"
  echo ""
  echo "--- Recent commits on master ---"
  git log --oneline -8
  echo ""
  echo "--- Last 6 progress snapshots ---"
  tail -6 "$PROGRESS_LOG"
  echo ""
  echo "Logs:"
  echo "  /tmp/chain_27b_phaseB.log"
  echo "  /tmp/chain_coder_phaseB.log"
  echo "  /tmp/chain_27b_nothink_grid.log"
  echo "  /tmp/chain_progress.log  (5-min snapshots)"
  echo "  /tmp/chain_watchdog.log  (watchdog events)"
}

# === Main loop ===
log "watchdog started; chain pids: ${CHAIN_PIDS[*]}"

while true; do
  vllm_health_check
  cleanup_zombie_sandboxes
  snapshot_progress
  hourly_commit

  any_alive=0
  for pid in "${CHAIN_PIDS[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then any_alive=1; break; fi
  done

  if (( any_alive == 0 )); then
    end_of_night
    log "watchdog exiting normally"
    break
  fi

  sleep "$LOOP_INTERVAL"
done
