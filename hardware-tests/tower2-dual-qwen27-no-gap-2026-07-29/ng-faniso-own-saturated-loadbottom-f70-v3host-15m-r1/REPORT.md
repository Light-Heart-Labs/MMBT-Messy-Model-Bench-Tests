# Bottom-card own-fan isolation at 70% - replicate 1

- Source run: `2026-07-30T22-38-56Z-ng-faniso-own-saturated-loadbottom-f70-v3host-15m-r1`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F70-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 1, sequence 3 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible candidate, n=1/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.993 W | 22.128 W |
| Mean / maximum temperature | 50.814 / 53 C | 39.388 / 40 C |
| Last-five-minute temperature | 51.048 C | 40.000 C |
| Fan duty / mean physical RPM | 70% / 2,157.122 | 50% / 1,678.145 |
| Mean / last-five-minute graphics clock | 1,025.235 / 1,021.903 MHz | 180.356 / 180.500 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.810 seconds mean
request duration. Its closing five one-minute temperature medians were exactly
51/51/51/51/51 C. Workload isolation, fixed-fan target tracking, physical RPM
telemetry, independent NVML clock sampling, power saturation, steady state, and
automatic cleanup all passed. No software thermal, hardware thermal, or
hardware power-brake event was sampled, and all corresponding slowdown
counters remained at zero.

Relative to the 30% cell, the loaded card was 5.635 C cooler on its
whole-window mean and the idle top neighbor was 5.590 C cooler. Despite that
cooling, loaded-card mean clock was 0.499 MHz lower and mean request duration
was 0.025 seconds higher. This first-block result is consistent with a
temperature benefit plus a possible high-RPM board-power/control tradeoff, but
it does not establish that mechanism until the Latin-order R2 and R3 blocks
remove the current 30-to-50-to-70 execution-order alias.
