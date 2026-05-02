#!/usr/bin/env bash
# Dual-GPU switchover orchestrator (2026-05-02).
#
# When the Coder Phase B chain finishes, free GPU1 and bring up a SECOND
# vllm-qwen36-awq instance there so the no-think grid runs on both GPUs in
# parallel. Sequence is designed to keep at least one chain pid alive in
# /tmp/chain_pids.txt at all times so the watchdog never sees an "all dead"
# state during transition (would trigger premature end_of_night).
#
# Sequence:
#   1. Wait for Coder Phase B chain pid (passed as $1) to exit.
#   2. Stop vllm-coder-next (frees GPU1).
#   3. Launch vllm-qwen36-awq-gpu1 on GPU1 / port 8003.
#   4. Wait for new endpoint ready.
#   5. Launch shard 1 on port 8003 → SHARD1_PID.
#   6. Update /tmp/chain_pids.txt = "<old nothink pid> <SHARD1_PID>"
#      (transition window — old chain still alive, both endpoints serving).
#   7. Kill old nothink chain pid (passed as $2). Orphans the in-flight harness
#      child on port 8002 — let it finish naturally.
#   8. Wait for orphan harness to finish (so shard 0 doesn't race on its
#      sandbox name).
#   9. Launch shard 0 on port 8002 → SHARD0_PID.
#  10. Update /tmp/chain_pids.txt = "<SHARD0_PID> <SHARD1_PID>"
#
# Usage: bash switchover_to_dual_gpu.sh <coder_pid> <nothink_pid>

set -u
SWITCHOVER_LOG=/tmp/switchover.log
CHAIN_PIDS_FILE=/tmp/chain_pids.txt

if [ $# -lt 2 ]; then
  echo "Usage: $0 <coder_pid> <nothink_pid>"
  exit 1
fi
CODER_PID=$1
NOTHINK_PID=$2

log() {
  printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$SWITCHOVER_LOG"
}

log "=== switchover orchestrator started ==="
log "CODER_PID=$CODER_PID NOTHINK_PID=$NOTHINK_PID"

# 1. Wait for Coder Phase B chain to exit
log "step 1: waiting for Coder Phase B chain pid $CODER_PID to exit..."
while kill -0 "$CODER_PID" 2>/dev/null; do
  sleep 30
done
log "step 1: Coder Phase B chain exited"

# 2. Stop vllm-coder-next
log "step 2: stopping vllm-coder-next..."
docker stop vllm-coder-next >>"$SWITCHOVER_LOG" 2>&1 || log "  vllm-coder-next stop returned non-zero (might already be down)"
docker rm vllm-coder-next >>"$SWITCHOVER_LOG" 2>&1 || true
log "step 2: vllm-coder-next torn down"

# 3. Launch vllm-qwen36-awq-gpu1 on GPU1:8003
log "step 3: launching vllm-qwen36-awq-gpu1 on GPU1:8003..."
docker run -d \
  --name vllm-qwen36-awq-gpu1 \
  --gpus '"device=1"' \
  --shm-size 8g \
  -v /home/michael/models:/models:ro \
  -p 127.0.0.1:8003:8000 \
  vllm/vllm-openai:latest \
  --model /models/cyankiwi-Qwen3.6-27B-AWQ-INT4 \
  --served-model-name qwen3.6-27b-awq \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.92 \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml >>"$SWITCHOVER_LOG" 2>&1
log "step 3: vllm-qwen36-awq-gpu1 launch issued"

# 4. Wait for new endpoint ready (up to 5 min)
log "step 4: waiting for port 8003 ready..."
waited=0
while (( waited < 300 )); do
  if curl -sf -m 5 http://127.0.0.1:8003/v1/models >/dev/null 2>&1; then
    log "step 4: port 8003 ready after ${waited}s"
    break
  fi
  sleep 5; waited=$((waited+5))
done
if (( waited >= 300 )); then
  log "step 4: ERROR — port 8003 did not become ready within 5 min; aborting switchover"
  log "step 4: dumping vllm-qwen36-awq-gpu1 last 30 log lines:"
  docker logs --tail 30 vllm-qwen36-awq-gpu1 >>"$SWITCHOVER_LOG" 2>&1
  exit 2
fi

# 5. Launch shard 1 on port 8003
log "step 5: launching shard 1 of 2 on port 8003..."
cd /home/michael/bench
nohup bash agent-pilot/scripts/run_full_grid_27b_nothink_shard.sh 1 2 8003 \
  > /tmp/chain_27b_nothink_shard1.log 2>&1 &
SHARD1_PID=$!
log "step 5: shard 1 pid=$SHARD1_PID"

# 6. Update chain pids: include old nothink pid + new shard 1 (transition window)
echo "$NOTHINK_PID $SHARD1_PID" > "$CHAIN_PIDS_FILE"
log "step 6: updated $CHAIN_PIDS_FILE = '$NOTHINK_PID $SHARD1_PID' (transition window)"

# 7. Kill old nothink chain bash. Orphan its in-flight harness on port 8002.
log "step 7: killing old nothink chain bash $NOTHINK_PID (orphans in-flight harness)..."
kill "$NOTHINK_PID" 2>/dev/null || log "  kill returned non-zero (might already be gone)"
sleep 2
if kill -0 "$NOTHINK_PID" 2>/dev/null; then
  log "  PID $NOTHINK_PID still alive after SIGTERM; sending SIGKILL"
  kill -KILL "$NOTHINK_PID" 2>/dev/null || true
fi
log "step 7: old nothink chain bash gone"

# 8. Wait for orphan harness to finish (max 30 min sanity cap; testwrite typical
# is 10-15 min, so 30 min is generous).
log "step 8: waiting for orphan nothink harness on port 8002 to finish..."
waited=0
while (( waited < 1800 )); do
  if ! ps aux | grep -E "python3.*harness\.py.*27b-nothink" | grep -v grep | grep -q .; then
    log "step 8: no orphan nothink harness running after ${waited}s"
    break
  fi
  sleep 30; waited=$((waited+30))
done
if (( waited >= 1800 )); then
  log "step 8: WARN — orphan still running after 30 min; proceeding anyway (shard 0 will skip if sandbox up)"
fi

# 9. Launch shard 0 on port 8002
log "step 9: launching shard 0 of 2 on port 8002..."
nohup bash agent-pilot/scripts/run_full_grid_27b_nothink_shard.sh 0 2 8002 \
  > /tmp/chain_27b_nothink_shard0.log 2>&1 &
SHARD0_PID=$!
log "step 9: shard 0 pid=$SHARD0_PID"

# 10. Final pids file
echo "$SHARD0_PID $SHARD1_PID" > "$CHAIN_PIDS_FILE"
log "step 10: updated $CHAIN_PIDS_FILE = '$SHARD0_PID $SHARD1_PID'"

log "=== switchover complete ==="
echo ""
echo "Now running:"
echo "  shard 0 (port 8002 / GPU0): pid $SHARD0_PID  log /tmp/chain_27b_nothink_shard0.log"
echo "  shard 1 (port 8003 / GPU1): pid $SHARD1_PID  log /tmp/chain_27b_nothink_shard1.log"
echo ""
echo "vLLM endpoints:"
docker ps --filter name=vllm- --format '  {{.Names}} {{.Status}}'
