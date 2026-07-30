# Fixed-fan 250/250 W, bottom/top 30/70% - v2 replicate 2

- Run: `2026-07-30T06-53-44Z-ng-fan-b30-t70-sym250-v2-15m-r2`
- Cell: `NG-FAN-B30-T70-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Fan policy: 30% bottom / 70% top
- Result: **pass; internally admissible v2 replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.994 W |
| Mean / maximum temperature | 46.608 / 49 C | 56.856 / 60 C |
| Last-five-minute mean temperature | 47.037 C | 58.012 C |
| Mean physical fan RPM | 1,200.103 | 2,157.158 |
| Mean graphics clock | 816.324 MHz | 790.784 MHz |
| Completed request rate | 0.9600 req/s | 0.8889 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 58, 58, 58, 58, 58 C |

All v2 gates passed with zero slowdown/brake events. Relative to R1, mean
temperatures changed by -0.046/+0.260 C, clocks by -1.925/+0.350 MHz, and
throughput was identical. The top-minus-bottom clock gap remained large at
-25.540 MHz versus -27.815 MHz in R1.

The cell is now `n=2/3`. Its repeated result strengthens the finding that
top-biased fan allocation is less performance-balanced than the bottom-biased
policy at the same aggregate RPM.
