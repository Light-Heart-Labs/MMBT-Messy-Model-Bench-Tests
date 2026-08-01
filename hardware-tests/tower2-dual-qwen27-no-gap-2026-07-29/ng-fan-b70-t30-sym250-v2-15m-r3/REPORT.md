# Fixed-fan 250/250 W, bottom/top 70/30% - v2 replicate 3

- Run: `2026-07-30T08-50-09Z-ng-fan-b70-t30-sym250-v2-15m-r3`
- Cell: `NG-FAN-B70-T30-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.994 W |
| Mean / maximum temperature | 45.658 / 48 C | 56.353 / 59 C |
| Last-five-minute mean temperature | 45.938 C | 57.025 C |
| Mean physical fan RPM | 2,157.084 | 1,200.092 |
| Mean graphics clock | 803.949 MHz | 804.286 MHz |
| Completed request rate | 0.9600 req/s | 0.9244 req/s |
| V2 one-minute medians | 46, 46, 46, 46, 46 C | 57, 57, 57, 57, 57 C |

All v2 gates passed with zero slowdown/brake events. Relative to R2, mean
temperatures changed by +0.216/+0.082 C, clocks by +1.383/+1.694 MHz, and
throughput was identical. The top-minus-bottom mean clock gap was effectively
zero at +0.337 MHz.

The cell has reached three admissible, independently initialized execution
blocks and is internally validated for Tower2's no-gap configuration. Across
all three replicates, the bottom-biased policy repeated the same
0.9600/0.9244 requests/s split while keeping the two card clocks substantially
more balanced than the reverse allocation.
