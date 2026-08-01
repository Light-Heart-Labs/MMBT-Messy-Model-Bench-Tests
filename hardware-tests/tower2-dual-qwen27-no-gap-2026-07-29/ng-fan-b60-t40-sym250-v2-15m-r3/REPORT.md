# Fixed-fan 250/250 W, bottom/top 60/40% - v2 replicate 3

- Run: `2026-07-30T10-20-29Z-ng-fan-b60-t40-sym250-v2-15m-r3`
- Cell: `NG-FAN-B60-T40-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.995 W | 249.995 W |
| Mean / maximum temperature | 46.111 / 48 C | 57.254 / 60 C |
| Last-five-minute mean temperature | 46.233 C | 58.037 C |
| Mean physical fan RPM | 1,917.087 | 1,439.117 |
| Mean graphics clock | 809.822 MHz | 800.225 MHz |
| Completed request rate | 0.9956 req/s | 0.9244 req/s |
| V2 one-minute medians | 47, 46, 46, 46, 46 C | 58, 58, 58, 58, 58 C |

All v2 gates passed with zero slowdown/brake events. Relative to R2, mean
temperatures changed by +0.218/-0.065 C, clocks by +1.452/-0.534 MHz, and
throughput was identical.

Across all three runs, mean temperature is 45.973/57.285 C versus the frozen
piecewise-linear prediction of 45.953/57.008 C: errors of only +0.020/+0.277 C.
Mean clock is 808.742/800.729 MHz versus 807.484/799.877 MHz predicted. The
bottom clock mean conservatively retains R1's two confirmed 2,362 MHz
phase-boundary samples.

The 60/40 cell is internally validated at `n=3` and can replace its interpolated
value with a direct model knot. It is not transferable without calibrated
ambient and local-inlet measurements.
