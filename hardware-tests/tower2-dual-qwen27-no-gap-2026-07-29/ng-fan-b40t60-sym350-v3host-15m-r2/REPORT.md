# 350/350 W B40T60 fixed-fan measured run R2

- Run: `2026-07-31T09:36:37Z-ng-fan-b40t60-sym350-v3host-15m-r2`
- Cell: `NG-FAN-B40T60-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 40%, GPU1/top 60%
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.992 W | 349.992 W |
| Mean / last-5m / maximum temperature | 55.486 / 56.032 / 58 C | 70.618 / 72.037 / 74 C |
| Fan / mean RPM | 40% / 1,439.150 | 60% / 1,917.142 |
| Mean / last-5m graphics clock | 1,361.446 / 1,355.719 MHz | 1,230.351 / 1,218.212 MHz |
| Requests/s | 1.3867 | 1.2800 |
| Mean request duration | 23.235 s | 24.645 s |

Both GPUs held 100% utilization, reached steady state, and passed every
quality gate. Physical fan RPM tracked the reversed policy, primary and
independent clock streams agreed, workload accounting matched, and all
thermal and brake events and counter deltas were zero. Cleanup restored
normal Tower2 state.

Compared with the immediately preceding B60T40 cell, shifting the same
20 fan-percentage points from bottom to top raised top mean temperature by
0.658 C, lowered top mean clock by 11.823 MHz, and added 0.086 seconds of
top mean latency. The direction reproduces R1.
