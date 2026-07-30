# Fixed-fan 300/300 W, bottom/top 60/40% - V3HOST population replicate 3

- Run: `2026-07-30T19-55-42Z-ng-fan-b60-t40-sym300-v3host-15m-r5`
- Cell: `NG-FAN-B60-T40-SYM300-V3HOST-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible V3HOST population replicate 3 of 3**
- Naming note: the raw campaign-sequence label is `R5`; the validation
  registry counts it as V3HOST population replicate 3.

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.981 W | 299.993 W |
| Mean / maximum temperature | 53.813 / 57 C | 67.378 / 71 C |
| Last-five-minute mean temperature | 54.073 C | 68.535 C |
| Mean physical fan RPM | 1,917.084 | 1,439.096 |
| Mean graphics clock | 1,023.606 MHz | 973.940 MHz |
| Last-five-minute mean clock | 1,019.592 MHz | 967.339 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| Mean request duration | 26.851 s | 28.867 s |
| V2 one-minute medians | 54, 54, 54, 54, 54 C | 68, 68, 69, 69, 69 C |

All steady-state, workload-isolation, fan-control, and telemetry gates passed.
Hardware/software thermal-slowdown and hardware power-brake events were zero.
Final preflight state was 30/32 C GPUs, 55.9 C CPU Tctl, and 40.9 C hottest
NVMe, essentially identical to population replicate 2.

GPU0 recorded a sub-second request-boundary transient: the minimum sampled
utilization was 52%, minimum averaged board power was 279.54 W, and maximum
clock was 1,665 MHz. The independent sampler reproduced the event. Mean
utilization remained 99.973% and 99.94% of samples met at least 95% of target
power, so the run passes the frozen loaded-power gate. All last-five-minute
samples were clean at a 299.993 W mean. The transient is retained explicitly
and robust/late-window metrics should be preferred for fitted effects.

This run brings the 60/40 V3HOST cell to the required three internally
admissible replicates. The paired 40/60 cell and order-adjusted crossover
analysis remain required before validating the policy contrast.
