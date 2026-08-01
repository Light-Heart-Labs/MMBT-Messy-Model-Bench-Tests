# Fixed-fan 200/200 W, bottom/top 40/60% - v2 replicate 2

- Run: `2026-07-30T13-19-44Z-ng-fan-b40-t60-sym200-v2-15m-r2`
- Cell: `NG-FAN-B40-T60-SYM200-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 199.996 W | 199.995 W |
| Mean / maximum temperature | 42.275 / 45 C | 50.895 / 54 C |
| Last-five-minute mean temperature | 43.007 C | 52.013 C |
| Mean physical fan RPM | 1,439.099 | 1,917.195 |
| Mean graphics clock | 665.693 MHz | 662.323 MHz |
| Last-five-minute mean clock | 664.712 MHz | 661.755 MHz |
| Completed request rate | 0.6756 req/s | 0.6400 req/s |
| V2 one-minute medians | 43, 43, 43, 43, 43 C | 52, 52, 52, 52, 52 C |

All v2 gates passed with exact 40/60 fan tracking, 100% utilization, complete
telemetry, and zero slowdown/brake events. Total mean card-level fan speed was
3,356.294 RPM.

Relative to replicate 1, mean temperatures were +0.443 C bottom and +0.479 C
top despite identical power, fan RPM, and workload controls. The closing
minute-median plateaus were one degree higher on both cards. With no
calibrated ambient or local-inlet probe, this shared movement must remain a
session/block effect rather than being attributed to the fan policy.

The corresponding 60/40 replicate 2 is required before estimating block 2's
directional allocation contrast.
