# Fixed-fan 200/200 W, bottom/top 60/40% - v2 replicate 1

- Run: `2026-07-30T12-50-43Z-ng-fan-b60-t40-sym200-v2-15m-r1`
- Cell: `NG-FAN-B60-T40-SYM200-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 199.996 W | 199.995 W |
| Mean / maximum temperature | 41.094 / 43 C | 50.313 / 52 C |
| Last-five-minute mean temperature | 41.040 C | 50.965 C |
| Mean physical fan RPM | 1,917.097 | 1,439.116 |
| Mean graphics clock | 661.101 MHz | 666.436 MHz |
| Last-five-minute mean clock | 661.084 MHz | 665.689 MHz |
| Completed request rate | 0.6756 req/s | 0.6756 req/s |
| V2 one-minute medians | 41, 41, 41, 41, 41 C | 51, 51, 51, 51, 51 C |

All v2 gates passed with exact 60/40 fan tracking, 100% utilization, complete
telemetry, and zero slowdown/brake events. Total mean card-level fan speed was
3,356.213 RPM, only 0.005 RPM below the paired 40/60 run.

Relative to 40/60 replicate 1 at the same 200/200 W caps, 60/40 changed mean
temperature by -0.738 C bottom and -0.103 C top. It shifted 3.667 MHz away
from the bottom and 3.674 MHz to the top, leaving the two-card clock sum
unchanged to 0.007 MHz. The top completed-request rate increased from 0.6400
to 0.6756 requests/s, although fixed-window request counts remain quantized.

Compared with the validated 250 W 60/40-minus-40/60 effect, the first 200 W
pair has a similar bottom-local cooling direction but a much smaller
cross-card temperature effect. Two further pairs are required before treating
that apparent power interaction as validated.
