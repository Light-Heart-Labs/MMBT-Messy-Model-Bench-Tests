# Fixed-fan 250/250 W, bottom/top 40/60% - v2 replicate 3

- Run: `2026-07-30T11-50-08Z-ng-fan-b40-t60-sym250-v2-15m-r3`
- Cell: `NG-FAN-B40-T60-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 3 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.995 W | 249.995 W |
| Mean / maximum temperature | 46.706 / 49 C | 57.907 / 61 C |
| Last-five-minute mean temperature | 47.027 C | 58.960 C |
| Mean physical fan RPM | 1,439.110 | 1,917.148 |
| Mean graphics clock | 814.414 MHz | 796.395 MHz |
| Last-five-minute mean clock | 813.642 MHz | 795.306 MHz |
| Completed request rate | 0.9956 req/s | 0.9244 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 59, 59, 59, 59, 59 C |

All v2 gates passed with zero slowdown/brake events. Total mean card-level fan
speed was 3,356.258 RPM, within 0.005 RPM of the validated 50/50 policy mean.
Fan duty tracked the commanded 40/60% policy without error for the complete
measured window.

Across the three internally admissible runs, 40/60 averaged 46.694/57.856 C
and 814.472/795.645 MHz. The frozen v2 prediction missed those temperatures by
only +0.156/+0.584 C and clocks by +0.664/+1.432 MHz. The v1 prediction at
40/60 was identical; both prior artifacts remain immutable.

This closes the fifth matched-total-RPM policy at `n=3`. The complete block
supports a directional allocation response: moving equal aggregate fan RPM
toward the bottom card reduces both card temperatures and progressively
improves the top-minus-bottom clock balance at this 250/250 W operating point.
