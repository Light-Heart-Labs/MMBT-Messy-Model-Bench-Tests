# 400/400 W EQ60 fixed-fan safety bump

- Run: `2026-07-31T14-04-04Z-ng-fan-eq60-sym400-v3host-bump-r1`
- Cell: `NG-FAN-EQ60-SYM400-V3HOST-BUMP`
- Policy: GPU0/bottom 60%, GPU1/top 60%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.991 W |
| Mean / maximum temperature | 60.633 / 64 C | 72.874 / 76 C |
| Fan / mean RPM | 60% / 1,917.483 | 60% / 1,917.384 |
| Mean graphics clock | 1,763.771 MHz | 1,583.936 MHz |
| Requests/s | 1.6000 | 1.3333 |
| Mean request duration | 21.586 s | 22.372 s |

Both GPUs held 100% utilization and the requested power cap. Fan target
tracking, workload isolation, primary telemetry, and the independent NVML
clock stream passed. Thermal and hardware-power-brake event samples and
counter deltas were zero. The cell was only 120 measured seconds and retained
positive temperature slopes; it does not count toward `n`.
