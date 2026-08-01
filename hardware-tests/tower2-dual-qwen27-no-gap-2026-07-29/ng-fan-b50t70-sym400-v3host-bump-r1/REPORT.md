# 400/400 W B50T70 fixed-fan safety bump

- Run: `2026-07-31T14-26-42Z-ng-fan-b50t70-sym400-v3host-bump-r1`
- Cell: `NG-FAN-B50T70-SYM400-V3HOST-BUMP`
- Policy: GPU0/bottom 50%, GPU1/top 70%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.990 W | 399.992 W |
| Mean / maximum temperature | 58.327 / 62 C | 70.218 / 75 C |
| Fan / mean RPM | 50% / 1,678.599 | 70% / 2,157.574 |
| Mean graphics clock | 1,788.282 MHz | 1,611.296 MHz |
| Requests/s | 1.6000 | 1.3333 |
| Mean request duration | 21.513 s | 22.253 s |

Both GPUs held 100% utilization and the requested power cap. Fan target
tracking, workload isolation, primary telemetry, and the independent NVML
clock stream passed. Thermal and hardware-power-brake event samples and
counter deltas were zero. The cell was only 120 measured seconds and retained
positive temperature slopes; it does not count toward `n`.
