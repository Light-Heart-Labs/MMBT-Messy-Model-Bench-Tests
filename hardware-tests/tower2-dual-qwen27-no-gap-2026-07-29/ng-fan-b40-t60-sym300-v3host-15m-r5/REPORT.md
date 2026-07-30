# Fixed-fan 300/300 W, bottom/top 40/60% - V3HOST population replicate 3

- Run: `2026-07-30T20-31-39Z-ng-fan-b40-t60-sym300-v3host-15m-r5`
- Cell: `NG-FAN-B40-T60-SYM300-V3HOST-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally validated V3HOST population replicate 3 of 3**
- Naming note: the raw campaign-sequence label is `R5`; the validation
  registry counts it as V3HOST population replicate 3.

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.994 W | 299.993 W |
| Mean / maximum temperature | 53.824 / 57 C | 67.162 / 70 C |
| Last-five-minute mean temperature | 54.155 C | 68.207 C |
| Mean physical fan RPM | 1,439.078 | 1,917.113 |
| Mean graphics clock | 1,032.538 MHz | 968.790 MHz |
| Last-five-minute mean clock | 1,030.311 MHz | 962.959 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |

All steady-state, power, workload-isolation, fan-control, and telemetry gates
passed. Both GPUs remained at 100% utilization and their requested 300 W caps;
hardware/software thermal-slowdown and hardware power-brake events were zero.

This run began from 29/32 C GPUs, 55.0 C CPU Tctl, and 40.9 C hottest NVMe.
Together with the two prior admissible V3HOST runs it raises the 40/60 policy
cell to `n=3`. Its tightly matched crossover partner is the immediately prior
60/40 run. Block 3 shows essentially no thermal policy effect but repeats the
small clock/latency transfer between cards. The validated paired analysis
therefore treats the thermal advantage seen in block 2 as weak and
non-reproduced rather than as a confirmed 300 W effect.
