# Bottom-card own-fan isolation at 50% - replicate 2

- Source run: `2026-07-30T23-13-10Z-ng-faniso-own-saturated-loadbottom-f50-v3host-15m-r2`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F50-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 2, sequence 1 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible candidate, n=2/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.993 W | 22.550 W |
| Mean / maximum temperature | 53.059 / 56 C | 41.568 / 43 C |
| Last-five-minute temperature | 53.590 C | 42.263 C |
| Fan duty / mean physical RPM | 50% / 1,678.078 | 50% / 1,678.136 |
| Mean / last-five-minute graphics clock | 1,026.904 / 1,023.217 MHz | 180.301 / 180.355 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.733 seconds mean
request duration. Its closing temperature medians were 53/53/54/54/54 C and
passed the prospective quantized plateau rule. All power, workload-isolation,
fan/RPM, independent-clock, event-counter, and cleanup gates passed with zero
thermal or brake activity.

R2 rotated this cell from second to first. It tightly reproduced R1: mean
temperature differed by -0.278 C, last-five-minute temperature by +0.028 C,
mean clock by -1.879 MHz, and mean request duration by +0.028 seconds.
