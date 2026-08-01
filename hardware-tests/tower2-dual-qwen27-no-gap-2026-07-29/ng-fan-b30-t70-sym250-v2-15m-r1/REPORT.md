# Fixed-fan 250/250 W, bottom/top 30/70% - v2 replicate 1

- Run: `2026-07-30T05-53-48Z-ng-fan-b30-t70-sym250-v2-15m-r1`
- Cell: `NG-FAN-B30-T70-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: 30% bottom / 70% top
- Result: **pass; internally admissible v2 replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.995 W | 249.994 W |
| Mean / maximum temperature | 46.654 / 49 C | 56.596 / 59 C |
| Last-five-minute mean temperature | 47.010 C | 57.527 C |
| Mean physical fan RPM | 1,200.056 | 2,157.131 |
| Mean graphics clock | 818.249 MHz | 790.434 MHz |
| Completed request rate | 0.9600 req/s | 0.8889 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 57, 57, 58, 58, 58 C |
| V2 median range / slope | 0 C / 0 C/min | 1 C / +0.3 C/min |

All power, utilization, sample-completeness, isolation, fan telemetry,
fan-target tracking, event-counter, and v2 plateau gates passed. No software
thermal, hardware thermal, or hardware power-brake event occurred.

The paired 30/70 and 70/30 cells are matched to within 0.018 RPM in summed
card-level fan speed:

| Policy | Bottom RPM | Top RPM | Sum |
|---|---:|---:|---:|
| 70/30 | 2,157.131 | 1,200.074 | 3,357.205 |
| 30/70 | 1,200.056 | 2,157.131 | 3,357.187 |

Despite that effectively exact total-RPM match, 70/30 was 1.343 C cooler on
the bottom and 0.337 C cooler on the top. It also improved top mean graphics
clock by 11.780 MHz and top request rate from 0.8889 to 0.9244 req/s. The
bottom clock changed in the opposite direction, leaving the sum of both mean
clocks nearly constant: 1,608.882 MHz for 70/30 versus 1,608.683 MHz for
30/70.

This first paired result indicates that bottom-biased fan effort both improves
stack thermals and redistributes the nearly fixed aggregate clock budget
toward the hotter, disadvantaged top card. One plausible mechanism is that fan
electrical load is inside each card's board-power budget, so moving fan work to
the cooler card preserves top-card compute power; fan electrical watts are not
currently measured, so this is a hypothesis rather than an established causal
channel. Each policy remains `n=1/3`.
