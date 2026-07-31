# 400/400 W B60T40 fixed-fan safety bump

- Run: `2026-07-31T12:40:06Z-ng-fan-b60t40-sym400-v3host-bump-r1`
- Cell: `NG-FAN-B60T40-SYM400-V3HOST-BUMP`
- Policy: GPU0/bottom 60%, GPU1/top 40%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.993 W | 399.992 W |
| Mean / maximum temperature | 57.318 / 60 C | 71.165 / 77 C |
| Fan / mean RPM | 60% / 1,917.719 | 40% / 1,439.475 |
| Mean graphics clock | 1,792.462 MHz | 1,621.297 MHz |
| Requests/s | 1.6000 | 1.6000 |
| Mean request duration | 21.511 s | 22.226 s |

This lowest-top-fan case passed power, utilization, telemetry, RPM,
workload-isolation, independent-clock, and slowdown-counter gates. Peak top
temperature was 77 C, 19 C below the 96 C test cutoff. The transient cell
does not count toward `n`.
