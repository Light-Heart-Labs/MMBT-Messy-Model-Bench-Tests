# Bottom-card own-fan isolation at 30% - replicate 1

- Source run: `2026-07-30T21-41-07Z-ng-faniso-own-saturated-loadbottom-f30-v3host-15m-r1`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F30-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 1, sequence 1 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible candidate, n=1/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.993 W | 23.166 W |
| Mean / maximum temperature | 56.449 / 59 C | 44.978 / 46 C |
| Last-five-minute temperature | 56.915 C | 46.000 C |
| Fan duty / mean physical RPM | 30% / 1,200.100 | 50% / 1,678.189 |
| Mean / last-five-minute graphics clock | 1,025.734 / 1,023.009 MHz | 180.203 / 180.135 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.785 seconds mean
request duration. Its closing five one-minute temperature medians were
57/57/57/57/57 C. Workload isolation, fixed-fan target tracking, physical RPM
telemetry, independent NVML clock sampling, power saturation, steady state, and
automatic cleanup all passed. No software thermal, hardware thermal, or
hardware power-brake event was sampled, and all corresponding slowdown
counters remained at zero.

This run is the first member of a randomized three-replicate Latin-order block.
It may be used as an individual Tower2/no-gap observation, but fan-response
coefficients remain preliminary until the 30%, 50%, and 70% cells each reach
three admissible independent replicates.
