# 400/400 W EQ60 fixed-fan measured cell R1

- Run: `2026-07-31T15-12-03Z-ng-fan-eq60-sym400-v3host-15m-r1`
- Cell: `NG-FAN-EQ60-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 60%, GPU1/top 60%
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.993 W |
| Mean / last-5m / maximum temperature | 60.661 / 61.310 / 64 C | 75.957 / 77.428 / 80 C |
| Fan / mean RPM | 60% / 1,917.102 | 60% / 1,917.093 |
| Mean / last-5m graphics clock | 1,764.440 / 1,759.015 MHz | 1,537.000 / 1,514.442 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.588 s | 22.578 s |

Both GPUs passed the fixed-quantized steady-state, completeness, saturated
power, fan tracking, workload isolation, independent clock, and counter
gates. Thermal/brake event samples and within-run counter deltas were zero.
No calibrated ambient or local-inlet probes were present, so the replicate is
internal rather than transferable.
