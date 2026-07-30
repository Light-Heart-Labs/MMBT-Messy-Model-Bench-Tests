# Fixed-fan 250/250 W, 50/50% baseline - v2 replicate 1

- Run: `2026-07-30T04-57-26Z-ng-fan-eq50-sym250-v2-15m-r1`
- Cell: `NG-FAN-EQ50-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: 50% bottom / 50% top
- Result: **pass; internally admissible v2 replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.994 W |
| Mean / maximum temperature | 46.293 / 49 C | 57.541 / 60 C |
| Last-five-minute mean temperature | 47.012 C | 58.749 C |
| Mean physical fan RPM | 1,678.123 | 1,678.147 |
| Mean graphics clock | 811.635 MHz | 797.396 MHz |
| Completed request rate | 0.9956 req/s | 0.9244 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 58, 59, 59, 59, 59 C |
| V2 median range / slope | 0 C / 0 C/min | 1 C / +0.2 C/min |

All power, utilization, sample-completeness, isolation, fan telemetry,
fan-target tracking, event-counter, and v2 plateau gates passed. Both cards
held exactly 50% current/target duty during the measured window; card-level
mean physical RPM differed by only 0.024 RPM. No software thermal, hardware
thermal, or hardware power-brake event occurred.

At equal power and equal approximately 1,678 RPM fan speed, the top card
averaged 11.248 C hotter and 14.239 MHz lower. Compared descriptively with the
three 30/30% trajectories, equal 50% fan duty reduced the positional
temperature penalty by about 5.2 C, roughly halved the clock penalty, and
increased throughput on both cards. This v2 cell is a new protocol and is not
pooled with the earlier v1 cell.

This is the constant-100-percentage-point reference for the crossed 70/30 and
30/70 policies. Those cells will reveal whether the same aggregate commanded
fan effort is more valuable when applied to the bottom card, to the top card,
or evenly. Actual RPM is retained as the primary normalization variable.
