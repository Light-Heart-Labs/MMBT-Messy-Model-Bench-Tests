# 400/400 W B70T50 fixed-fan measured cell R2

- Run: `2026-07-31T16-59-14Z-ng-fan-b70t50-sym400-v3host-15m-r2`
- Cell: `NG-FAN-B70T50-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 70%, GPU1/top 50%
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.983 W | 399.992 W |
| Mean / last-5m / maximum temperature | 60.625 / 61.045 / 64 C | 75.890 / 77.058 / 80 C |
| Fan / mean RPM | 70% / 2,157.105 | 50% / 1,678.043 |
| Mean / last-5m graphics clock | 1,756.801 / 1,752.854 MHz | 1,545.220 / 1,526.716 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.613 s | 22.558 s |

Both GPUs held 100% utilization, reached a quantized steady-state plateau,
and passed isolation, telemetry, independent-clock, fan/RPM, power, and
counter gates. Thermal-slowdown and hardware-power-brake events and counter
deltas were zero.

Relative to direction-reversed B50T70 in the same R2 block, B70T50 reduced
bottom/top mean temperature by 1.018/0.853 C, raised top mean graphics clock
by 25.309 MHz, and reduced top mean request duration by 0.133 seconds.

