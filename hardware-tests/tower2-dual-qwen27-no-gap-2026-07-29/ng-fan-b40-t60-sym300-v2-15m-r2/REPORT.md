# Fixed-fan 300/300 W, bottom/top 40/60% - v2 replicate 2

- Run: `2026-07-30T16-19-15Z-ng-fan-b40-t60-sym300-v2-15m-r2`
- Cell: `NG-FAN-B40-T60-SYM300-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.993 W | 299.993 W |
| Mean / maximum temperature | 53.977 / 57 C | 67.473 / 71 C |
| Last-five-minute mean temperature | 54.654 C | 68.992 C |
| Mean physical fan RPM | 1,439.092 | 1,917.134 |
| Mean graphics clock | 1,030.363 MHz | 970.964 MHz |
| Last-five-minute mean clock | 1,027.122 MHz | 963.346 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| V2 one-minute medians | 54, 54, 55, 55, 55 C | 69, 69, 69, 69, 69 C |

All v2 gates passed with exact 40/60 fan tracking, 100% utilization, complete
telemetry, and zero hardware/software thermal-slowdown or hardware power-brake
events. Total mean card-level fan speed was 3,356.226 RPM.

Replicate 2 reproduced replicate 1 throughput exactly and differed by only
+0.321/+0.528 C and -2.291/-1.819 MHz bottom/top. It ran first in the reversed
block-2 order. Its late 1 C bottom rise still passed the prospective quantized
plateau rule. The paired 60/40 replicate is required before interpreting the
block-2 fan-policy contrast.
