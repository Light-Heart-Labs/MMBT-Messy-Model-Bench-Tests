# Bottom-card own-fan isolation at 50% - replicate 1

- Source run: `2026-07-30T22-11-10Z-ng-faniso-own-saturated-loadbottom-f50-v3host-15m-r1`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F50-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 1, sequence 2 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible candidate, n=1/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.993 W | 22.390 W |
| Mean / maximum temperature | 53.337 / 56 C | 41.876 / 43 C |
| Last-five-minute temperature | 53.562 C | 42.676 C |
| Fan duty / mean physical RPM | 50% / 1,678.064 | 50% / 1,678.169 |
| Mean / last-five-minute graphics clock | 1,028.783 / 1,026.112 MHz | 180.378 / 180.301 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.705 seconds mean
request duration. Its closing five one-minute temperature medians were
54/54/54/53/53 C. Workload isolation, fixed-fan target tracking, physical RPM
telemetry, independent NVML clock sampling, power saturation, steady state, and
automatic cleanup all passed. No software thermal, hardware thermal, or
hardware power-brake event was sampled, and all corresponding slowdown
counters remained at zero.

Relative to the preceding 30% cell, the loaded card was 3.112 C cooler on its
whole-window mean and 3.353 C cooler over the last five minutes. Its mean clock
was 3.049 MHz higher and mean request duration was 0.080 seconds lower. Those
within-block contrasts are preliminary because fan setting and execution order
are still aliased in replicate 1.
