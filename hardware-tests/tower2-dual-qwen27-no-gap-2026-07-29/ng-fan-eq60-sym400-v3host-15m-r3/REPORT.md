# 400/400 W EQ60 fixed-fan measured cell R3

- Run: `2026-07-31T20-39-31Z-ng-fan-eq60-sym400-v3host-15m-r3`
- Cell: `NG-FAN-EQ60-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 60%, GPU1/top 60%
- Result: **pass; internally admissible replicate 3 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.992 W |
| Mean / last-5m / maximum temperature | 62.736 / 63.340 / 66 C | 78.330 / 80.045 / 83 C |
| Fan / mean RPM | 60% / 1,917.089 | 60% / 1,917.075 |
| Mean / last-5m graphics clock | 1,747.531 / 1,740.148 MHz | 1,505.339 / 1,478.898 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.629 s | 22.768 s |

Both GPUs held 100% utilization, reached a quantized steady-state plateau,
and passed isolation, telemetry, independent-clock, fan/RPM, power, and
counter gates. Thermal-slowdown and hardware-power-brake events and counter
deltas were zero. This middle cell was hotter than its immediate neighbors,
underscoring why inference uses within-block direction-reversed pairs and a
rotated-order replicate design rather than unpaired policy means alone.

