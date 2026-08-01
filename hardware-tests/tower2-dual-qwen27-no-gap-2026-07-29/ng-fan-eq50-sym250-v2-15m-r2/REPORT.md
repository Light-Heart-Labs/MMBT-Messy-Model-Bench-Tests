# Fixed-fan 250/250 W, 50/50% baseline - v2 replicate 2

- Run: `2026-07-30T06-25-32Z-ng-fan-eq50-sym250-v2-15m-r2`
- Cell: `NG-FAN-EQ50-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Fan policy: 50% bottom / 50% top
- Result: **pass; internally admissible v2 replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.995 W |
| Mean / maximum temperature | 46.470 / 49 C | 57.771 / 61 C |
| Last-five-minute mean temperature | 47.028 C | 59.013 C |
| Mean physical fan RPM | 1,678.140 | 1,678.143 |
| Mean graphics clock | 810.685 MHz | 796.136 MHz |
| Completed request rate | 0.9956 req/s | 0.9244 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 59, 59, 59, 59, 59 C |

All v2 quality gates passed and all slowdown/brake counters remained zero.
Relative to R1, mean temperatures changed by only +0.177 C bottom and +0.230 C
top, mean clocks by -0.950 and -1.260 MHz, and throughput was identical. This
establishes tight two-replicate repeatability for the equal-fan reference.

The cell is now `n=2/3`. It remains internally useful but not transferable
without calibrated ambient and local-inlet measurements.
