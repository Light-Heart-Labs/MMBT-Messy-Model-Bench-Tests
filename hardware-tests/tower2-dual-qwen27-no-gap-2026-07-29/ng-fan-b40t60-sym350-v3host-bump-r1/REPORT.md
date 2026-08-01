# 350/350 W B40T60 fixed-fan safety bump

- Run: `2026-07-31T06-56-42Z-ng-fan-b40t60-sym350-v3host-bump-r1`
- Cell: `NG-FAN-B40T60-SYM350-V3HOST-BUMP`
- Policy: GPU0/bottom 40%, GPU1/top 60%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.993 W | 349.992 W |
| Mean / maximum temperature | 53.502 / 57 C | 65.620 / 70 C |
| Fan / mean RPM | 40% / 1,439.529 | 60% / 1,917.640 |
| Mean graphics clock | 1,372.932 MHz | 1,275.632 MHz |
| Requests/s | 1.3333 | 1.3333 |
| Mean request duration | 23.131 s | 24.279 s |

Both GPUs held 100% utilization. Fan target tracking, workload isolation,
primary telemetry, and the independent NVML clock stream passed. Thermal and
hardware-power-brake event samples and counter deltas were zero. The cell was
only 120 measured seconds and was not steady state; it does not count toward
`n`.
