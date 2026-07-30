# Fixed-fan 300/300 W, bottom/top 60/40% - V3HOST population replicate 1

- Run: `2026-07-30T17-29-24Z-ng-fan-b60-t40-sym300-v3host-15m-r3`
- Cell: `NG-FAN-B60-T40-SYM300-V3HOST-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible V3HOST population replicate 1 of 3**
- Naming note: the raw run configuration retains campaign-sequence replicate
  label `R3`; this is the first independently counted replicate in the new
  V3HOST population and is not pooled with the two earlier V2 runs.

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.994 W | 299.993 W |
| Mean / maximum temperature | 56.078 / 59 C | 69.658 / 74 C |
| Last-five-minute mean temperature | 57.039 C | 71.238 C |
| Mean physical fan RPM | 1,917.141 | 1,439.068 |
| Mean graphics clock | 1,013.750 MHz | 963.358 MHz |
| Last-five-minute mean clock | 1,009.197 MHz | 954.376 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| V2 one-minute medians | 57, 57, 57, 57, 57 C | 71, 71, 71, 71, 72 C |

All steady-state, power, workload-isolation, fan-control, and telemetry gates
passed. Both GPUs remained at 100% utilization and their requested 300 W caps;
hardware/software thermal-slowdown and hardware power-brake events were zero.
The top-minus-bottom mean differences were +13.580 C and -50.392 MHz.

This is the first run using the prospective whole-system reset gate. GPU core
conditions became eligible well before the hottest NVMe cooled to the 41.9 C
threshold. The harness waited about 9 minutes 45 seconds before the continuous
five-minute soak could begin, then completed 304 seconds without a reset.
Measurement therefore began from 32/34 C GPUs, 58.1 C CPU Tctl, and 41.9 C
hottest NVMe. This run must be compared only with other V3HOST runs when
estimating policy effects.

During load, host CPU Tctl averaged 87.248 C and reached 89.6 C; the hottest
NVMe averaged 44.933 C and reached 46.9 C. These host values are retained as
potential chassis-heat covariates. The generated
[`thermal-stress.png`](thermal-stress.png) and complete raw telemetry preserve
the run for paired and mixed-effects analysis.
