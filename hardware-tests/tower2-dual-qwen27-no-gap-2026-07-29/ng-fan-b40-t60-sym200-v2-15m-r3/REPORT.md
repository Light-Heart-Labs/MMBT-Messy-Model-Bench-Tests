# Fixed-fan 200/200 W, bottom/top 40/60% - v2 replicate 3

- Run: `2026-07-30T14-48-06Z-ng-fan-b40-t60-sym200-v2-15m-r3`
- Cell: `NG-FAN-B40-T60-SYM200-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 199.995 W | 199.996 W |
| Mean / maximum temperature | 43.712 / 46 C | 52.361 / 55 C |
| Last-five-minute mean temperature | 44.020 C | 53.030 C |
| Mean physical fan RPM | 1,439.100 | 1,917.125 |
| Mean graphics clock | 663.819 MHz | 661.108 MHz |
| Last-five-minute mean clock | 662.356 MHz | 660.846 MHz |
| Completed request rate | 0.6756 req/s | 0.6400 req/s |
| V2 one-minute medians | 44, 44, 44, 44, 44 C | 53, 53, 53, 53, 53 C |

All v2 gates passed with exact 40/60 fan tracking, 100% utilization, complete
telemetry, and zero hardware/software thermal-slowdown or hardware power-brake
events. Total mean card-level fan speed was 3,356.225 RPM.

This was deliberately run second in block 3 after the 60/40 policy, reversing
the order used in blocks 1 and 2. Compared with the immediately preceding
60/40 run, this later run was +0.974 C bottom and +0.864 C top. Because this
warmer-second-run contrast reverses the apparent thermal policy effect seen in
block 1, execution order/session heat is an important nuisance variable.
Calibrated inlet probes are still required before treating sub-degree policy
differences as transferable chassis effects.
