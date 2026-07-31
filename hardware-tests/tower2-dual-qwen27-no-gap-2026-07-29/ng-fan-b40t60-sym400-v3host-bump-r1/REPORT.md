# 400/400 W B40T60 fixed-fan safety bump

- Run: `2026-07-31T12:25:07Z-ng-fan-b40t60-sym400-v3host-bump-r1`
- Cell: `NG-FAN-B40T60-SYM400-V3HOST-BUMP`
- Policy: GPU0/bottom 40%, GPU1/top 60%
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 399.990 W | 399.992 W |
| Mean / maximum temperature | 58.023 / 62 C | 71.491 / 76 C |
| Fan / mean RPM | 40% / 1,439.674 | 60% / 1,917.686 |
| Mean graphics clock | 1,797.899 MHz | 1,607.134 MHz |
| Requests/s | 1.6000 | 1.3333 |
| Mean request duration | 21.501 s | 22.287 s |

Both GPUs held 100% utilization and passed every qualification gate with zero
thermal or hardware-power-brake events. The 120-second cell was thermally
transient and does not count toward `n`.
