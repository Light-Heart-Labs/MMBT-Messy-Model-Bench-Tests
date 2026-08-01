# 400/400 W B70T50 fixed-fan measured cell R3

- Run: `2026-07-31T21-17-21Z-ng-fan-b70t50-sym400-v3host-15m-r3`
- Cell: `NG-FAN-B70T50-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 70%, GPU1/top 50%
- Result: **pass; internally admissible replicate 3 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.992 W |
| Mean / last-5m / maximum temperature | 61.517 / 61.065 / 65 C | 76.941 / 77.359 / 81 C |
| Fan / mean RPM | 70% / 2,157.112 | 50% / 1,678.081 |
| Mean / last-5m graphics clock | 1,748.733 / 1,750.970 MHz | 1,525.054 / 1,517.116 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.645 s | 22.647 s |

Both GPUs held 100% utilization, reached a quantized steady-state plateau,
and passed isolation, telemetry, independent-clock, fan/RPM, power, and
counter gates. Thermal-slowdown and hardware-power-brake events and counter
deltas were zero.

Relative to direction-reversed B50T70 in the same R3 block, B70T50 reduced
top last-five-minute temperature by 0.688 C, raised top last-five-minute
graphics clock by 20.591 MHz, and reduced top whole-window request duration
by 0.029 seconds. The steady-state directions reproduce R1 and R2.

