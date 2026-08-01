# 400/400 W B70T50 fixed-fan measured cell R1

- Run: `2026-07-31T15-46-33Z-ng-fan-b70t50-sym400-v3host-15m-r1`
- Cell: `NG-FAN-B70T50-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 70%, GPU1/top 50%
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.992 W |
| Mean / last-5m / maximum temperature | 60.474 / 61.003 / 64 C | 75.733 / 77.027 / 80 C |
| Fan / mean RPM | 70% / 2,157.112 | 50% / 1,678.069 |
| Mean / last-5m graphics clock | 1,755.908 / 1,751.800 MHz | 1,547.256 / 1,528.122 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.599 s | 22.539 s |

Both GPUs passed the fixed-quantized steady-state, completeness, saturated
power, fan tracking, workload isolation, independent clock, and counter
gates. Thermal/brake event samples and within-run counter deltas were zero.
No calibrated ambient or local-inlet probes were present, so the replicate is
internal rather than transferable.
