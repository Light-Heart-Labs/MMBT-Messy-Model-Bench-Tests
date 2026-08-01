# Fixed-fan 250/250 W, bottom/top 60/40% - v2 replicate 2

- Run: `2026-07-30T09-51-42Z-ng-fan-b60-t40-sym250-v2-15m-r2`
- Cell: `NG-FAN-B60-T40-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.995 W |
| Mean / maximum temperature | 45.893 / 48 C | 57.319 / 60 C |
| Last-five-minute mean temperature | 46.035 C | 58.030 C |
| Mean physical fan RPM | 1,917.112 | 1,439.121 |
| Mean graphics clock | 808.370 MHz | 800.759 MHz |
| Completed request rate | 0.9956 req/s | 0.9244 req/s |
| V2 one-minute medians | 46, 46, 46, 46, 46 C | 58, 58, 58, 58, 58 C |

All v2 gates passed with zero slowdown/brake events. Relative to R1, mean
temperatures changed by -0.022/+0.036 C, clocks by +0.335/-0.444 MHz, and
throughput was identical. R1's two greater-than-2 GHz GPU0 phase-boundary
samples did not recur.

The cell is now `n=2/3`. Its mean observed-minus-predicted temperature error
across R1/R2 is approximately -0.05/+0.29 C, supporting the bounded
interpolator while preserving the need for a third run.
