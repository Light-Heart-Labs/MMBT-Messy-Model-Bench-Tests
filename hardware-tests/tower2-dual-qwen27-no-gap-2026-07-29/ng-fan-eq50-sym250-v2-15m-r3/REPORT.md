# Fixed-fan 250/250 W, bottom/top 50/50% - v2 replicate 3

- Run: `2026-07-30T07-51-39Z-ng-fan-eq50-sym250-v2-15m-r3`
- Cell: `NG-FAN-EQ50-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.995 W |
| Mean / maximum temperature | 46.543 / 49 C | 57.854 / 61 C |
| Last-five-minute mean temperature | 47.028 C | 59.028 C |
| Mean physical fan RPM | 1,678.099 | 1,678.137 |
| Mean graphics clock | 809.403 MHz | 796.636 MHz |
| Completed request rate | 0.9956 req/s | 0.9244 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 59, 59, 59, 59, 59 C |

All v2 gates passed with zero slowdown/brake events. Relative to R2, mean
temperatures changed by +0.073/+0.083 C, clocks by -1.282/+0.500 MHz, and
throughput was identical. The cell has now reached three admissible,
independently initialized execution blocks and is internally validated for this
Tower2 no-gap configuration. It is not transferable without calibrated ambient
and local-inlet measurements.
