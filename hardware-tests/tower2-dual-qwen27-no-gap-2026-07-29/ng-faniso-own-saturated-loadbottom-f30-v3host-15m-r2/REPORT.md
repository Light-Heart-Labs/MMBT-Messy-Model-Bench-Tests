# Bottom-card own-fan isolation at 30% - replicate 2

- Source run: `2026-07-31T00-08-51Z-ng-faniso-own-saturated-loadbottom-f30-v3host-15m-r2`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F30-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 2, sequence 3 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible candidate, n=2/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.994 W | 23.378 W |
| Mean / maximum temperature | 55.717 / 58 C | 44.249 / 45 C |
| Last-five-minute temperature | 55.990 C | 45.000 C |
| Fan duty / mean physical RPM | 30% / 1,200.081 | 50% / 1,678.179 |
| Mean / last-five-minute graphics clock | 1,027.351 / 1,025.006 MHz | 180.379 / 180.450 MHz |
| GPU utilization | 99.987% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.772 seconds mean
request duration. Its closing five one-minute temperature medians were exactly
56/56/56/56/56 C. Workload isolation, fixed-fan target tracking, physical RPM
telemetry, independent NVML clock sampling, power saturation, steady state, and
automatic cleanup all passed. No software thermal, hardware thermal, or
hardware power-brake event was sampled, and all corresponding counters
remained at zero.

R2 rotated this cell from first to last in its three-cell block. It remained
the warmest condition, confirming that the large thermal ordering is not an
artifact of R1 execution order. Its clock relationship to 50% changed
direction, so 30-versus-50 performance remains unresolved until R3.
