# 350/350 W EQ50 fixed-fan measured run R1

- Run: `2026-07-31T07:40:21Z-ng-fan-eq50-sym350-v3host-15m-r1`
- Cell: `NG-FAN-EQ50-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 50%, GPU1/top 50%
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.993 W | 349.992 W |
| Mean / last-5m / maximum temperature | 55.471 / 56.047 / 59 C | 71.193 / 72.922 / 75 C |
| Fan / mean RPM | 50% / 1,678.135 | 50% / 1,678.148 |
| Mean / last-5m graphics clock | 1,362.526 / 1,356.179 MHz | 1,230.757 / 1,214.222 MHz |
| Requests/s | 1.3511 | 1.2800 |
| Mean request duration | 23.278 s | 24.657 s |

Both GPUs held 100% utilization and reached the fixed-fan quantized
steady-state plateau. Primary and independent NVML clocks agreed, workload
accounting matched the controlled request log, fan targets tracked with zero
percentage-point error, and all sampled software-thermal, hardware-thermal,
and hardware-power-brake events and counter deltas were zero. Automatic fan
control, 600 W limits, production containers, and user services were restored.

The top card's last-five-minute temperature was 16.875 C above the bottom and
its clock was 141.957 MHz lower. This is the equal-duty R1 reference; policy
inference requires the two order-rotated blocks.
