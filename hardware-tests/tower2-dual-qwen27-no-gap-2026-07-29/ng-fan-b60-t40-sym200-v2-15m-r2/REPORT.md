# Fixed-fan 200/200 W, bottom/top 60/40% - v2 replicate 2

- Run: `2026-07-30T13-48-14Z-ng-fan-b60-t40-sym200-v2-15m-r2`
- Cell: `NG-FAN-B60-T40-SYM200-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 199.996 W | 199.996 W |
| Mean / maximum temperature | 42.359 / 44 C | 51.374 / 54 C |
| Last-five-minute mean temperature | 42.940 C | 52.025 C |
| Mean physical fan RPM | 1,917.053 | 1,439.103 |
| Mean graphics clock | 660.823 MHz | 665.417 MHz |
| Last-five-minute mean clock | 660.764 MHz | 664.867 MHz |
| Completed request rate | 0.6756 req/s | 0.6756 req/s |
| V2 one-minute medians | 43, 43, 43, 43, 43 C | 52, 52, 52, 52, 52 C |

All v2 gates passed with exact 60/40 fan tracking, 100% utilization, complete
telemetry, and zero slowdown/brake events. Total mean card-level fan speed was
3,356.156 RPM.

Relative to its preceding 40/60 block-2 run, this later 60/40 run was +0.084 C
bottom and +0.479 C top. That thermal sign differs from block 1, while clocks
again moved from the bottom card to the top and the top-minus-bottom gap
improved by 7.964 MHz. Host CPU and storage temperatures were also higher in
the later run.

The contradictory small thermal contrast is retained rather than averaged
away. Block 3 reverses execution order (60/40 first, then 40/60) to expose
time/order bias. Calibrated inlet probes remain necessary for transferable
sub-degree claims.
