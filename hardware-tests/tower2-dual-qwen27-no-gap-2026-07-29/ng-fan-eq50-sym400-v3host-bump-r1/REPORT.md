# 400/400 W EQ50 fixed-fan safety bump

- Run: `2026-07-31T12:09:58Z-ng-fan-eq50-sym400-v3host-bump-r1`
- Cell: `NG-FAN-EQ50-SYM400-V3HOST-BUMP`
- Policy: GPU0/bottom 50%, GPU1/top 50%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.994 W | 399.992 W |
| Mean / maximum temperature | 57.965 / 62 C | 71.588 / 76 C |
| Fan / mean RPM | 50% / 1,678.777 | 50% / 1,678.702 |
| Mean graphics clock | 1,801.678 MHz | 1,606.784 MHz |
| Requests/s | 1.6000 | 1.3583 |
| Mean request duration | 21.492 s | 22.126 s |

Both GPUs held 100% utilization and passed power, fan/RPM, workload-isolation,
independent-clock, telemetry, and slowdown-counter gates. The 120-second cell
was still warming and does not count toward `n`.
