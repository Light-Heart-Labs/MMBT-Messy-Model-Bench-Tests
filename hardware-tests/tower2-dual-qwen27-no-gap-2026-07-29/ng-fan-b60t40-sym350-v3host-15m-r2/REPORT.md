# 350/350 W B60T40 fixed-fan measured run R2

- Run: `2026-07-31T09:08:49Z-ng-fan-b60t40-sym350-v3host-15m-r2`
- Cell: `NG-FAN-B60T40-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 60%, GPU1/top 40%
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.992 W | 349.992 W |
| Mean / last-5m / maximum temperature | 54.510 / 55.055 / 58 C | 69.960 / 71.649 / 74 C |
| Fan / mean RPM | 60% / 1,917.125 | 40% / 1,439.105 |
| Mean / last-5m graphics clock | 1,358.727 / 1,353.005 MHz | 1,242.174 / 1,229.670 MHz |
| Requests/s | 1.3511 | 1.2800 |
| Mean request duration | 23.258 s | 24.559 s |

Both GPUs held 100% utilization, reached the fixed-fan quantized steady-state
plateau, and passed workload-isolation, telemetry, independent-clock,
fan-tracking, power, and counter gates. All thermal and hardware-power-brake
events and counter deltas were zero; cleanup restored normal Tower2 state.

This policy ran first rather than second in R2. Its top mean temperature,
clock, and latency differed from R1 by only +0.065 C, -0.084 MHz, and
+0.008 seconds, respectively, demonstrating strong order-independent
repeatability.
