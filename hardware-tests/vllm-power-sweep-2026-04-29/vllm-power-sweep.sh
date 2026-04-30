#!/bin/bash
# vLLM throughput-vs-power sweep on GPU1.
# For each cap: 5-min sustained N-concurrent load, log requests + power/temp.
# Requires: vllm-qwen36-awq running on :8000.

set -u
CAPS="${CAPS:-600 550 500 450 400 350 300}"
DURATION="${DURATION:-300}"
CONCURRENCY="${CONCURRENCY:-32}"
MAX_TOKENS="${MAX_TOKENS:-200}"
ENDPOINT="${ENDPOINT:-http://127.0.0.1:8000/v1/chat/completions}"
MODEL="${MODEL:-qwen3.6-27b-awq}"

STAMP=$(date +%Y-%m-%d-%H%M)
OUTDIR=~/thermal-tests/vllm-sweep-$STAMP
mkdir -p "$OUTDIR"
SUMMARY="$OUTDIR/summary.txt"
exec > >(tee "$OUTDIR/run.log") 2>&1

PROMPT='Write a detailed technical analysis of distributed-systems consensus algorithms, covering Paxos, Raft, and Byzantine fault tolerance. Discuss tradeoffs between safety and liveness, leader election, log replication, and quorum requirements. Be precise and verbose.'
PAYLOAD=$(jq -nc --arg m "$MODEL" --arg p "$PROMPT" --argjson mt $MAX_TOKENS \
  '{model:$m,messages:[{role:"user",content:$p}],max_tokens:$mt,temperature:0.7,stream:false}')

cleanup() {
  echo "--- cleanup ---"
  pkill -P $$ 2>/dev/null
  jobs -p | xargs -r kill 2>/dev/null
}
trap cleanup EXIT INT TERM

worker() {
  local id=$1 logfile=$2 endtime=$3
  while [ "$(date +%s)" -lt "$endtime" ]; do
    local t0 t1 resp tok
    t0=$(date +%s.%N)
    resp=$(curl -sS -m 120 -X POST "$ENDPOINT" -H 'Content-Type: application/json' -d "$PAYLOAD" 2>/dev/null)
    t1=$(date +%s.%N)
    tok=$(echo "$resp" | jq -r '.usage.completion_tokens // 0' 2>/dev/null)
    [ -z "$tok" ] && tok=0
    echo "$id,$t0,$t1,$tok" >> "$logfile"
  done
}

power_logger() {
  local outfile=$1 endtime=$2
  while [ "$(date +%s)" -lt "$endtime" ]; do
    nvidia-smi --query-gpu=index,power.draw,temperature.gpu,clocks.current.graphics,utilization.gpu \
      --format=csv,noheader,nounits -i 1 | awk -v ts="$(date +%s)" -F, '{print ts","$0}' >> "$outfile"
    sleep 2
  done
}

echo "=== vLLM power sweep started $STAMP ==="
echo "caps=$CAPS  duration=${DURATION}s  concurrency=$CONCURRENCY  max_tokens=$MAX_TOKENS"
echo "outdir=$OUTDIR"
echo
printf "%-6s %8s %8s %10s %10s %8s %8s %8s\n" "cap" "req" "tokens" "agg_tps" "tps_per" "pwr_W" "temp_C" "MHz" | tee -a "$SUMMARY"
printf "%-6s %8s %8s %10s %10s %8s %8s %8s\n" "------" "--------" "--------" "----------" "----------" "--------" "--------" "--------" | tee -a "$SUMMARY"

for CAP in $CAPS; do
  echo
  echo "=== CAP $CAP W start $(date +%H:%M:%S) ==="
  sudo nvidia-smi -i 1 -pl $CAP >/dev/null
  sleep 3

  LOG="$OUTDIR/load_${CAP}w.csv"
  PWR="$OUTDIR/power_${CAP}w.csv"
  : > "$LOG"
  : > "$PWR"

  END=$(($(date +%s) + DURATION))

  power_logger "$PWR" "$END" &
  PWR_PID=$!

  WORKER_PIDS=()
  for i in $(seq 1 $CONCURRENCY); do
    worker $i "$LOG" "$END" &
    WORKER_PIDS+=($!)
  done

  wait $PWR_PID
  for pid in "${WORKER_PIDS[@]}"; do
    wait "$pid" 2>/dev/null
  done

  REQ=$(wc -l < "$LOG")
  TOK=$(awk -F, '{s+=$4} END{print s+0}' "$LOG")
  SPAN=$(awk -F, 'NR==1{min=$2} {if($2<min)min=$2; if($3>max)max=$3} END{printf "%.2f", max-min}' "$LOG")
  AGG=$(awk -v t=$TOK -v s=$SPAN 'BEGIN{if(s>0) printf "%.1f", t/s; else print "0"}')
  PER=$(awk -v a=$AGG -v c=$CONCURRENCY 'BEGIN{printf "%.2f", a/c}')
  PWRMEAN=$(awk -F, '{p+=$3} END{if(NR>0) printf "%.1f", p/NR; else print "0"}' "$PWR")
  TEMPMEAN=$(awk -F, '{t+=$4} END{if(NR>0) printf "%.1f", t/NR; else print "0"}' "$PWR")
  MHZMEAN=$(awk -F, '{m+=$5} END{if(NR>0) printf "%.0f", m/NR; else print "0"}' "$PWR")

  printf "%-6s %8s %8s %10s %10s %8s %8s %8s\n" "${CAP}W" "$REQ" "$TOK" "$AGG" "$PER" "$PWRMEAN" "$TEMPMEAN" "$MHZMEAN" | tee -a "$SUMMARY"
done

echo
echo "=== restoring GPU1 to 500W ==="
sudo nvidia-smi -i 1 -pl 500 >/dev/null
nvidia-smi --query-gpu=index,power.limit --format=csv

echo
echo "=== outputs in $OUTDIR ==="
echo "summary:"
cat "$SUMMARY"
