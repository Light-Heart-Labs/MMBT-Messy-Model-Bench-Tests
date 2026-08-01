# Bottom-card own-fan isolation at 30% - replicate 3

- Source run: `2026-07-31T01-07-26Z-ng-faniso-own-saturated-loadbottom-f30-v3host-15m-r3`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F30-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 3, sequence 2 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible, n=3/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.993 W | 22.334 W |
| Mean / maximum temperature | 53.469 / 56 C | 41.893 / 43 C |
| Last-five-minute temperature | 54.020 C | 43.000 C |
| Fan duty / mean physical RPM | 30% / 1,200.099 | 50% / 1,678.219 |
| Mean / last-five-minute graphics clock | 1,040.615 / 1,037.221 MHz | 180.326 / 180.163 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.581 seconds mean
request duration. Its closing minute medians were 54/54/54/54/54 C. All
power, workload-isolation, fan/RPM, independent-clock, event-counter, and
cleanup gates passed with zero thermal or brake activity.

This was the second cell in the completed Latin-order R3 block. Its cooler
absolute operating point relative to R1/R2 is retained as evidence of a
block/session heat-state shift; the paired within-block fan contrasts remain
the inferential unit.
