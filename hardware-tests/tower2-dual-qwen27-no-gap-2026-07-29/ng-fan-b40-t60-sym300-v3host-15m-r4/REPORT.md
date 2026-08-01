# Fixed-fan 300/300 W, bottom/top 40/60% - V3HOST population replicate 2

- Run: `2026-07-30T18-43-57Z-ng-fan-b40-t60-sym300-v3host-15m-r4`
- Cell: `NG-FAN-B40-T60-SYM300-V3HOST-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible V3HOST population replicate 2 of 3**
- Naming note: the raw campaign-sequence label is `R4`; the validation
  registry counts it as V3HOST population replicate 2.

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 299.993 W | 299.993 W |
| Mean / maximum temperature | 54.484 / 57 C | 67.785 / 71 C |
| Last-five-minute mean temperature | 55.015 C | 69.027 C |
| Mean physical fan RPM | 1,439.075 | 1,917.133 |
| Mean graphics clock | 1,028.289 MHz | 967.079 MHz |
| Last-five-minute mean clock | 1,024.636 MHz | 960.007 MHz |
| Completed request rate | 1.2089 req/s | 1.1022 req/s |
| V2 one-minute medians | 55, 55, 55, 55, 55 C | 69, 69, 69, 69, 69 C |

All steady-state, power, workload-isolation, fan-control, and telemetry gates
passed. Both GPUs remained at 100% utilization and their requested 300 W caps;
hardware/software thermal-slowdown and hardware power-brake events were zero.

This run began from 30/32 C GPUs, 54.8 C CPU Tctl, and 40.9 C hottest NVMe.
Relative to V3HOST population replicate 1, bottom/top mean temperature changed
by only +0.051/+0.052 C, graphics clock by -0.378/+0.493 MHz, loaded CPU Tctl
by -0.197 C, and loaded hottest-NVMe temperature by +0.010 C. Request rates
were identical. This is tight within-policy and whole-system-state
reproduction; one additional independent replicate is required for validation.
