# 400/400 W B50T70 fixed-fan measured cell R2

- Run: `2026-07-31T17-34-30Z-ng-fan-b50t70-sym400-v3host-15m-r2`
- Cell: `NG-FAN-B50T70-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 50%, GPU1/top 70%
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.992 W |
| Mean / last-5m / maximum temperature | 61.643 / 62.048 / 65 C | 76.743 / 78.038 / 81 C |
| Fan / mean RPM | 50% / 1,678.102 | 70% / 2,157.055 |
| Mean / last-5m graphics clock | 1,766.085 / 1,759.319 MHz | 1,519.911 / 1,502.296 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.570 s | 22.691 s |

Both GPUs held 100% utilization, reached a quantized steady-state plateau,
and passed isolation, telemetry, independent-clock, fan/RPM, power, and
counter gates. Thermal-slowdown and hardware-power-brake events and counter
deltas were zero.

Despite assigning the top GPU 70% local fan, this direction-reversed policy
left it 0.853 C hotter and 25.309 MHz slower than B70T50 in the same block.
That paired direction is consistent with upstream/lower-card fan assistance.

