# Fixed-fan 200/200 W, bottom/top 40/60% - v2 replicate 1

- Run: `2026-07-30T12-22-15Z-ng-fan-b40-t60-sym200-v2-15m-r1`
- Cell: `NG-FAN-B40-T60-SYM200-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 199.996 W | 199.996 W |
| Mean / maximum temperature | 41.832 / 44 C | 50.416 / 53 C |
| Last-five-minute mean temperature | 42.035 C | 51.060 C |
| Mean physical fan RPM | 1,439.104 | 1,917.114 |
| Mean graphics clock | 664.768 MHz | 662.762 MHz |
| Last-five-minute mean clock | 665.106 MHz | 662.075 MHz |
| Completed request rate | 0.6756 req/s | 0.6400 req/s |
| V2 one-minute medians | 42, 42, 42, 42, 42 C | 51, 51, 51, 51, 51 C |

All v2 gates passed with exact 40/60 fan tracking, 100% utilization, complete
telemetry, and zero slowdown/brake events. Total mean card-level fan speed was
3,356.218 RPM.

Relative to the validated 250/250 W 40/60 mean, reducing each cap by 50 W
reduced mean temperature by 4.862 C bottom and 7.440 C top. The positional
temperature gap narrowed from 11.162 C to 8.584 C, while the top-minus-bottom
clock gap narrowed from -18.827 MHz to -2.006 MHz. This single replicate
suggests nonlinear power dependence but is not yet a validated power effect.

The paired 60/40 cell and two further independently initialized replicates per
policy are required before estimating the 200 W fan-allocation effect.
