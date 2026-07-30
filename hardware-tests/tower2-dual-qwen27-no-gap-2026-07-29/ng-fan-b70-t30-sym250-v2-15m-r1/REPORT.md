# Fixed-fan 250/250 W, bottom/top 70/30% - v2 replicate 1

- Run: `2026-07-30T05-25-49Z-ng-fan-b70-t30-sym250-v2-15m-r1`
- Cell: `NG-FAN-B70-T30-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: 70% bottom / 30% top
- Result: **pass; internally admissible v2 replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.995 W |
| Mean / maximum temperature | 45.311 / 48 C | 56.259 / 59 C |
| Last-five-minute mean temperature | 45.255 C | 57.010 C |
| Mean physical fan RPM | 2,157.131 | 1,200.074 |
| Mean graphics clock | 806.668 MHz | 802.214 MHz |
| Completed request rate | 0.9600 req/s | 0.9244 req/s |
| V2 one-minute medians | 45, 45, 45, 45, 46 C | 57, 57, 57, 57, 57 C |
| V2 median range / slope | 1 C / +0.2 C/min | 0 C / 0 C/min |

All power, utilization, sample-completeness, isolation, fan telemetry,
fan-target tracking, event-counter, and v2 plateau gates passed. No software
thermal, hardware thermal, or hardware power-brake event occurred.

The paired 70/30 and 50/50 cells are unusually well matched in total physical
fan speed:

| Policy | Bottom RPM | Top RPM | Sum |
|---|---:|---:|---:|
| 50/50 | 1,678.123 | 1,678.147 | 3,356.270 |
| 70/30 | 2,157.131 | 1,200.074 | 3,357.205 |

The total differs by only 0.935 RPM, or 0.028%. At that essentially identical
aggregate RPM, moving fan work from the top card to the bottom reduced mean
bottom temperature by 0.982 C and mean top temperature by 1.282 C. The top
clock increased by 4.818 MHz and the top-minus-bottom clock deficit narrowed
from -14.239 to -4.454 MHz.

This is direct preliminary evidence that bottom-card fan work assists the top
card through the shared no-gap airflow path. It supports the proposed
cooperative policy and contradicts a model in which only each card's own fan
speed matters. It remains `n=1/3`, lacks calibrated inlet/ambient probes, and
requires the reverse 30/70 policy plus replication before optimization claims
are promoted.
