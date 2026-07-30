# Fixed-fan 250/250 W, bottom/top 30/70% - v2 replicate 3

- Run: `2026-07-30T08-20-50Z-ng-fan-b30-t70-sym250-v2-15m-r3`
- Cell: `NG-FAN-B30-T70-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.995 W |
| Mean / maximum temperature | 46.661 / 49 C | 57.012 / 60 C |
| Last-five-minute mean temperature | 47.027 C | 58.012 C |
| Mean physical fan RPM | 1,200.101 | 2,157.123 |
| Mean graphics clock | 816.553 MHz | 793.893 MHz |
| Completed request rate | 0.9600 req/s | 0.8889 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 58, 58, 58, 58, 58 C |

All v2 gates passed with zero slowdown/brake events. Relative to R2, mean
temperatures changed by +0.053/+0.156 C, clocks by +0.229/+3.109 MHz, and
throughput was identical. The top-minus-bottom mean clock gap remained large at
-22.660 MHz.

The cell has reached three admissible, independently initialized execution
blocks and is internally validated for Tower2's no-gap configuration. Across
all three replicates, allocating the larger share of the matched RPM budget to
the top card produced the same 0.9600/0.8889 requests/s split.
