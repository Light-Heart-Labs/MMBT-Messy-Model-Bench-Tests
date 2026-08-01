# Fixed-fan 300/300 W, bottom/top 60/40% - v2 replicate 2

- Run: `2026-07-30T16-48-21Z-ng-fan-b60-t40-sym300-v2-15m-r2`
- Cell: `NG-FAN-B60-T40-SYM300-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.993 W | 299.993 W |
| Mean / maximum temperature | 54.840 / 59 C | 68.397 / 73 C |
| Last-five-minute mean temperature | 56.043 C | 70.478 C |
| Mean physical fan RPM | 1,917.161 | 1,439.089 |
| Mean graphics clock | 1,018.666 MHz | 970.758 MHz |
| Last-five-minute mean clock | 1,013.549 MHz | 960.273 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| V2 one-minute medians | 56, 56, 56, 56, 56 C | 70, 70, 70, 71, 71 C |

All v2 gates passed with exact 60/40 fan tracking, 100% utilization, complete
telemetry, and zero hardware/software thermal-slowdown or hardware power-brake
events. Total mean card-level fan speed was 3,356.250 RPM.

This run followed the 40/60 replicate in reversed-order block 2. The raw
60/40-minus-40/60 contrast was +0.863/+0.924 C and -11.697/-0.206 MHz
bottom/top; request rates were identical. The policy run second was warmer in
both block 1 and block 2, despite reversing which policy ran second. This is
direct evidence that accumulated chassis/session heat can dominate the raw
temperature contrast. The paired policy effect must be order-adjusted.
