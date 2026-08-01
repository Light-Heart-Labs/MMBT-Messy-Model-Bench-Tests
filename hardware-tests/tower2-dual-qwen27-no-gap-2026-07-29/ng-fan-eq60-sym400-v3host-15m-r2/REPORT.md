# 400/400 W EQ60 fixed-fan measured cell R2

- Run: `2026-07-31T18-10-32Z-ng-fan-eq60-sym400-v3host-15m-r2`
- Cell: `NG-FAN-EQ60-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 60%, GPU1/top 60%
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.991 W |
| Mean / last-5m / maximum temperature | 61.600 / 62.037 / 65 C | 76.881 / 78.050 / 81 C |
| Fan / mean RPM | 60% / 1,917.094 | 60% / 1,917.065 |
| Mean / last-5m graphics clock | 1,759.747 / 1,754.356 MHz | 1,523.197 / 1,504.671 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.614 s | 22.673 s |

Both GPUs held 100% utilization, reached a quantized steady-state plateau,
and passed isolation, telemetry, independent-clock, fan/RPM, power, and
counter gates. Thermal-slowdown and hardware-power-brake events and counter
deltas were zero. EQ60 ran third in R2 and remains the equal-allocation
reference for the 120-point fan budget.

