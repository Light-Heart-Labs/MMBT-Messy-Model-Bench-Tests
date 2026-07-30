# Fixed-fan 300/300 W, bottom/top 40/60% - V3HOST population replicate 1

- Run: `2026-07-30T18-07-23Z-ng-fan-b40-t60-sym300-v3host-15m-r3`
- Cell: `NG-FAN-B40-T60-SYM300-V3HOST-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible V3HOST population replicate 1 of 3**
- Naming note: the raw run configuration retains campaign-sequence replicate
  label `R3`; this is the first independently counted replicate in the new
  V3HOST population and is not pooled with the two earlier V2 runs.

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.993 W | 299.993 W |
| Mean / maximum temperature | 54.433 / 57 C | 67.733 / 71 C |
| Last-five-minute mean temperature | 55.033 C | 69.037 C |
| Mean physical fan RPM | 1,439.089 | 1,917.130 |
| Mean graphics clock | 1,028.667 MHz | 966.586 MHz |
| Last-five-minute mean clock | 1,026.291 MHz | 958.548 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| V2 one-minute medians | 55, 55, 55, 55, 55 C | 69, 69, 69, 69, 69 C |

All steady-state, power, workload-isolation, fan-control, and telemetry gates
passed. Both GPUs remained at 100% utilization and their requested 300 W caps;
hardware/software thermal-slowdown and hardware power-brake events were zero.
The top-minus-bottom mean differences were +13.300 C and -62.081 MHz.

This run used the prospective whole-system reset gate. The harness waited about
6 minutes 25 seconds for the hottest NVMe to reach the 41.9 C threshold, then
completed 304 seconds of continuous soak. Measurement setup began from 29/32 C
GPUs, 58.1 C CPU Tctl, and 40.9 C hottest NVMe.

Relative to the preceding 60/40 V3HOST run, this 40/60 run was cooler by
1.645/1.925 C and faster by 14.917/3.228 MHz bottom/top, with identical request
rates. Its start and loaded host states were also cooler, so this raw difference
is not a causal fan-policy estimate. See
[`analysis/300W_V3HOST_FAN_POLICY_BLOCK1.md`](../analysis/300W_V3HOST_FAN_POLICY_BLOCK1.md)
for the covariate-preserving paired analysis.
