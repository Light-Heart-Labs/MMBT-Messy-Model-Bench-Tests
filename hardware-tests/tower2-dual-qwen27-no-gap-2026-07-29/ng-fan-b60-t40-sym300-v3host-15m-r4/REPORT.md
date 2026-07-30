# Fixed-fan 300/300 W, bottom/top 60/40% - V3HOST population replicate 2

- Run: `2026-07-30T19-19-56Z-ng-fan-b60-t40-sym300-v3host-15m-r4`
- Cell: `NG-FAN-B60-T40-SYM300-V3HOST-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible V3HOST population replicate 2 of 3**
- Naming note: the raw campaign-sequence label is `R4`; the validation
  registry counts it as V3HOST population replicate 2.

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.993 W | 299.993 W |
| Mean / maximum temperature | 53.707 / 57 C | 67.277 / 71 C |
| Last-five-minute mean temperature | 54.080 C | 68.611 C |
| Mean physical fan RPM | 1,917.063 | 1,439.101 |
| Mean graphics clock | 1,021.504 MHz | 973.041 MHz |
| Last-five-minute mean clock | 1,018.503 MHz | 966.165 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| Mean request duration | 26.864 s | 28.914 s |
| V2 one-minute medians | 54, 54, 54, 54, 54 C | 68, 68.5, 69, 69, 69 C |

All steady-state, power, workload-isolation, fan-control, and telemetry gates
passed. Both GPUs remained at 100% utilization and their requested 300 W caps;
hardware/software thermal-slowdown and hardware power-brake events were zero.

This run completed tightly matched crossover block 2. Relative to the
immediately preceding 40/60 run, 60/40 made the bottom/top cards
0.777/0.508 C cooler while moving -6.785/+5.962 MHz of mean clock between
them. Combined mean clock changed by only -0.823 MHz, combined
last-five-minute clock by +0.025 MHz, and request rates were identical.
Bottom/top mean request duration changed by +0.123/-0.154 seconds,
directionally matching the clock redistribution.

Final preflight states differed by 0/0 C GPU, +1.2 C CPU Tctl, and 0 C NVMe;
loaded CPU and NVMe means differed by -0.197 and -0.698 C. The block meets the
prospective matched-pair tolerances. See
[`analysis/300W_V3HOST_FAN_POLICY_BLOCK2.md`](../analysis/300W_V3HOST_FAN_POLICY_BLOCK2.md).
