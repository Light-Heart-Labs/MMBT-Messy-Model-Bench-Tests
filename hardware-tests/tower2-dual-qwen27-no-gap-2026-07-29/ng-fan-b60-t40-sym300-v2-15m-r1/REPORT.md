# Fixed-fan 300/300 W, bottom/top 60/40% - v2 replicate 1

- Run: `2026-07-30T15-20-21Z-ng-fan-b60-t40-sym300-v2-15m-r1`
- Cell: `NG-FAN-B60-T40-SYM300-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.993 W | 299.993 W |
| Mean / maximum temperature | 52.679 / 55 C | 66.109 / 70 C |
| Last-five-minute mean temperature | 53.042 C | 67.107 C |
| Mean physical fan RPM | 1,917.118 | 1,439.108 |
| Mean graphics clock | 1,027.379 MHz | 982.287 MHz |
| Last-five-minute mean clock | 1,023.347 MHz | 976.049 MHz |
| Completed request rate | 1.2089 req/s | 1.1378 req/s |
| V2 one-minute medians | 53, 53, 53, 53, 53 C | 67, 67, 67, 67, 67 C |

All v2 gates passed with exact 60/40 fan tracking, 100% utilization, complete
telemetry, and zero hardware/software thermal-slowdown or hardware power-brake
events. Total mean card-level fan speed was 3,356.226 RPM.

At the same total fan-RPM budget used by the validated 200 W and 250 W fan
allocation cells, raising both cards to 300 W produced a 13.430 C top-minus-
bottom mean temperature gap and a -45.092 MHz top-minus-bottom clock gap.
These are replicate-1 observations, not validated effects. A paired 40/60 run
and at least two more replicates per policy are required before estimating the
power-by-allocation interaction.
