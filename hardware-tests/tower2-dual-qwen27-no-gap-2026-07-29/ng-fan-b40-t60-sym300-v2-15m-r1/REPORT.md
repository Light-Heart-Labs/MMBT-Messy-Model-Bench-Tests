# Fixed-fan 300/300 W, bottom/top 40/60% - v2 replicate 1

- Run: `2026-07-30T15-50-38Z-ng-fan-b40-t60-sym300-v2-15m-r1`
- Cell: `NG-FAN-B40-T60-SYM300-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.994 W | 299.993 W |
| Mean / maximum temperature | 53.656 / 56 C | 66.945 / 71 C |
| Last-five-minute mean temperature | 54.045 C | 68.050 C |
| Mean physical fan RPM | 1,439.104 | 1,917.125 |
| Mean graphics clock | 1,032.654 MHz | 972.783 MHz |
| Last-five-minute mean clock | 1,026.540 MHz | 966.588 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| V2 one-minute medians | 54, 54, 54, 54, 54 C | 68, 68, 68, 68, 68 C |

All v2 gates passed with exact 40/60 fan tracking, 100% utilization, complete
telemetry, and zero hardware/software thermal-slowdown or hardware power-brake
events. Total mean card-level fan speed was 3,356.229 RPM.

This run followed the 60/40 replicate in block 1. The raw 60/40-minus-40/60
contrast was -0.977/-0.836 C bottom/top and -5.275/+9.504 MHz. Because the
later 40/60 run was both warmer and slower on the top card despite 478 more top
RPM, the raw contrast is confounded by execution order/session heat. It is not
evidence that more top fan causes worse thermals or performance. Alternating
order and further replication are required.
