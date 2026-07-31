# 400/400 W B50T70 fixed-fan measured cell R3

- Run: `2026-07-31T20-03-44Z-ng-fan-b50t70-sym400-v3host-15m-r3`
- Cell: `NG-FAN-B50T70-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 50%, GPU1/top 70%
- Result: **pass; internally admissible replicate 3 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.990 W | 399.992 W |
| Mean / last-5m / maximum temperature | 61.544 / 62.055 / 66 C | 76.592 / 78.047 / 81 C |
| Fan / mean RPM | 50% / 1,678.125 | 70% / 2,157.054 |
| Mean / last-5m graphics clock | 1,765.821 / 1,760.835 MHz | 1,519.349 / 1,496.525 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.560 s | 22.676 s |

Both GPUs held 100% utilization, reached a quantized steady-state plateau,
and passed isolation, telemetry, independent-clock, fan/RPM, power, and
counter gates. Thermal-slowdown and hardware-power-brake events and counter
deltas were zero.

