# 400/400 W B70T50 fixed-fan safety bump

- Run: `2026-07-31T14-44-25Z-ng-fan-b70t50-sym400-v3host-bump-r1`
- Cell: `NG-FAN-B70T50-SYM400-V3HOST-BUMP`
- Policy: GPU0/bottom 70%, GPU1/top 50%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.992 W |
| Mean / maximum temperature | 58.006 / 62 C | 70.351 / 74 C |
| Fan / mean RPM | 70% / 2,157.802 | 50% / 1,678.492 |
| Mean graphics clock | 1,774.998 MHz | 1,619.146 MHz |
| Requests/s | 1.6000 | 1.6000 |
| Mean request duration | 21.553 s | 22.217 s |

Both GPUs held 100% utilization and the requested power cap. Fan target
tracking, workload isolation, primary telemetry, and the independent NVML
clock stream passed. Thermal and hardware-power-brake event samples and
counter deltas were zero. The cell was only 120 measured seconds and retained
positive temperature slopes; it does not count toward `n`.
