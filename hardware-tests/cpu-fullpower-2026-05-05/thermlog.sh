#!/bin/bash
# Sampling logger — appends a CSV row every 2s with CPU/GPU/NVMe thermals.
# Usage: ./thermlog.sh >> logfile.csv &   (write header first; kill with pkill -f thermlog.sh)
while true; do
  T=$(date +%H:%M:%S)
  S=$(sensors 2>/dev/null)
  TCTL=$(echo "$S" | awk '/Tctl/{v=$2; gsub(/[+°C]/,"",v); print v; exit}')
  CCDMAX=$(echo "$S" | awk '/Tccd/{v=$2; gsub(/[+°C]/,"",v); if(v+0>m)m=v+0} END{printf "%.1f",m}')
  NVME=$(echo "$S" | awk '/^Composite/{v=$2; gsub(/[+°C]/,"",v); printf "%s,",v}')
  GPU=$(nvidia-smi --query-gpu=temperature.gpu,power.draw,clocks.current.graphics,fan.speed,utilization.gpu --format=csv,noheader,nounits 2>/dev/null | paste -sd'|')
  G0=$(echo "$GPU" | cut -d'|' -f1 | tr -d ' ')
  G1=$(echo "$GPU" | cut -d'|' -f2 | tr -d ' ')
  CPUMHZ=$(awk '/cpu MHz/{s+=$4;n++} END{printf "%.0f", (n?s/n:0)}' /proc/cpuinfo)
  echo "$T,$TCTL,$CCDMAX,$CPUMHZ,$G0,$G1,${NVME%,}"
  sleep 2
done
