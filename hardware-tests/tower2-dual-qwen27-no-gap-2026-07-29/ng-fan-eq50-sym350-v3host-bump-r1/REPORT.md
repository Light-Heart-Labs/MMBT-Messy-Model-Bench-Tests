# 350/350 W EQ50 fixed-fan safety bump

- Run: `2026-07-31T06-41-45Z-ng-fan-eq50-sym350-v3host-bump-r1`
- Cell: `NG-FAN-EQ50-SYM350-V3HOST-BUMP`
- Policy: GPU0/bottom 50%, GPU1/top 50%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.991 W | 349.992 W |
| Mean / maximum temperature | 53.678 / 57 C | 66.087 / 71 C |
| Fan / mean RPM | 50% / 1,678.574 | 50% / 1,678.674 |
| Mean graphics clock | 1,367.921 MHz | 1,280.045 MHz |
| Requests/s | 1.3333 | 1.3333 |
| Mean request duration | 23.184 s | 24.221 s |

Both GPUs held 100% utilization. Fan target tracking, workload isolation,
primary telemetry, and the independent NVML clock stream passed. Thermal and
hardware-power-brake event samples and counter deltas were zero. The cell was
only 120 measured seconds and was not steady state; it does not count toward
`n`.
