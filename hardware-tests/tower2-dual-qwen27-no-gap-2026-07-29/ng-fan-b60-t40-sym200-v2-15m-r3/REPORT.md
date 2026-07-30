# Fixed-fan 200/200 W, bottom/top 60/40% - v2 replicate 3

- Run: `2026-07-30T14-17-56Z-ng-fan-b60-t40-sym200-v2-15m-r3`
- Cell: `NG-FAN-B60-T40-SYM200-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 199.996 W | 199.996 W |
| Mean / maximum temperature | 42.738 / 45 C | 51.497 / 54 C |
| Last-five-minute mean temperature | 43.022 C | 52.027 C |
| Mean physical fan RPM | 1,917.087 | 1,439.114 |
| Mean graphics clock | 660.993 MHz | 664.109 MHz |
| Last-five-minute mean clock | 660.928 MHz | 662.954 MHz |
| Completed request rate | 0.6756 req/s | 0.6400 req/s |
| V2 one-minute medians | 43, 43, 43, 43, 43 C | 52, 52, 52, 52, 52 C |

All v2 gates passed with exact 60/40 fan tracking, 100% utilization, complete
telemetry, and zero hardware/software thermal-slowdown or hardware power-brake
events. Total mean card-level fan speed was 3,356.201 RPM.

This was deliberately run first in block 3, reversing the order used in blocks
1 and 2. Its means were +1.644 C bottom and +1.184 C top relative to replicate
1, demonstrating material session/heat-soak drift even though each run reached
a flat five-minute temperature plateau. The following 40/60 run provides the
paired crossover contrast. Without calibrated inlet probes, sub-degree thermal
policy effects remain internal and potentially confounded by execution order.
