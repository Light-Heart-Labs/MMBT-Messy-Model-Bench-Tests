# 400/400 W B50T70 fixed-fan measured cell R1

- Run: `2026-07-31T16-22-14Z-ng-fan-b50t70-sym400-v3host-15m-r1`
- Cell: `NG-FAN-B50T70-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 50%, GPU1/top 70%
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.972 W | 399.991 W |
| Mean / last-5m / maximum temperature | 61.373 / 62.047 / 65 C | 76.300 / 77.988 / 81 C |
| Fan / mean RPM | 50% / 1,678.116 | 70% / 2,157.061 |
| Mean / last-5m graphics clock | 1,767.890 / 1,758.208 MHz | 1,528.079 / 1,504.512 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.562 s | 22.647 s |

Both GPUs passed the fixed-quantized steady-state, completeness, saturated
power, fan tracking, workload isolation, independent clock, and counter
gates. Thermal/brake event samples and within-run counter deltas were zero.
GPU0 had a 0.5-second admitted request-boundary transient at 380.77 W and
2,662 MHz, reproduced by both clock streams; it remained at 100% sampled
utilization and above the 380 W gate. No calibrated ambient or local-inlet
probes were present, so the replicate is internal rather than transferable.
