# Fixed-fan 250/250 W, bottom/top 70/30% - v2 replicate 2

- Run: `2026-07-30T07-21-35Z-ng-fan-b70-t30-sym250-v2-15m-r2`
- Cell: `NG-FAN-B70-T30-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Fan policy: 70% bottom / 30% top
- Result: **pass; internally admissible v2 replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.995 W | 249.994 W |
| Mean / maximum temperature | 45.442 / 48 C | 56.271 / 59 C |
| Last-five-minute mean temperature | 46.022 C | 57.038 C |
| Mean physical fan RPM | 2,157.087 | 1,200.089 |
| Mean graphics clock | 802.566 MHz | 802.592 MHz |
| Completed request rate | 0.9600 req/s | 0.9244 req/s |
| V2 one-minute medians | 46, 46, 46, 46, 46 C | 57, 57, 57, 57, 57 C |

All v2 gates passed with zero slowdown/brake events. Relative to R1, mean
temperatures changed by +0.131/+0.012 C, clocks by -4.102/+0.378 MHz, and
throughput was identical. The top-minus-bottom mean clock gap was effectively
zero at +0.026 MHz versus -4.454 MHz in R1.

The cell is now `n=2/3`. It repeats R1's thermal operating point almost exactly
and continues to support the hypothesis that placing more of a fixed aggregate
fan-RPM budget on the bottom card assists the adjacent stack. A third replicate
is required before treating the policy comparison as internally validated.
