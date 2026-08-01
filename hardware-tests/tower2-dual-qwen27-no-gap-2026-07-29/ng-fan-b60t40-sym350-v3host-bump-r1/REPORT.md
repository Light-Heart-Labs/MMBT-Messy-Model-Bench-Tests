# 350/350 W B60T40 fixed-fan safety bump

- Run: `2026-07-31T07-11-34Z-ng-fan-b60t40-sym350-v3host-bump-r1`
- Cell: `NG-FAN-B60T40-SYM350-V3HOST-BUMP`
- Policy: GPU0/bottom 60%, GPU1/top 40%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.992 W | 349.993 W |
| Mean / maximum temperature | 52.872 / 56 C | 65.285 / 70 C |
| Fan / mean RPM | 60% / 1,917.946 | 40% / 1,439.640 |
| Mean graphics clock | 1,364.674 MHz | 1,285.826 MHz |
| Requests/s | 1.3333 | 1.3333 |
| Mean request duration | 23.227 s | 24.164 s |

Both GPUs held 100% utilization. Fan target tracking, workload isolation,
primary telemetry, and the independent NVML clock stream passed. Thermal and
hardware-power-brake event samples and counter deltas were zero. The cell was
only 120 measured seconds and was not steady state; it does not count toward
`n`.
