# 400/400 W EQ50 fixed-fan measured run R1

- Run: `2026-07-31T12:58:43Z-ng-fan-eq50-sym400-v3host-15m-r1`
- Cell: `NG-FAN-EQ50-SYM400-V3HOST-15M`
- Policy: GPU0/bottom 50%, GPU1/top 50%
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.992 W | 399.991 W |
| Mean / last-5m / maximum temperature | 61.114 / 62.053 / 65 C | 79.197 / 81.529 / 84 C |
| Fan / mean RPM | 50% / 1,678.165 | 50% / 1,678.099 |
| Mean / last-5m graphics clock | 1,765.768 / 1,755.809 MHz | 1,500.929 / 1,465.490 MHz |
| Requests/s | 1.4933 | 1.4222 |
| Mean request duration | 21.545 s | 22.818 s |

Both GPUs held 100% utilization and passed saturated-power, steady-state,
workload-isolation, fan/RPM tracking, independent-clock, completeness, and
counter gates. Thermal and hardware-power-brake events and counter deltas were
zero. The top-card maximum was only 1 C below the static-spine 85 C cutoff, so
EQ50 is admissible evidence but not a robust deployment recommendation.
