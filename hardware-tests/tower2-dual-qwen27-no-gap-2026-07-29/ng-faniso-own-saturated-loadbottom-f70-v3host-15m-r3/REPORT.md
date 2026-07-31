# Bottom-card own-fan isolation at 70% - replicate 3

- Source run: `2026-07-31T00-39-40Z-ng-faniso-own-saturated-loadbottom-f70-v3host-15m-r3`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F70-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 3, sequence 1 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible, n=3/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.993 W | 20.961 W |
| Mean / maximum temperature | 48.912 / 51 C | 37.518 / 39 C |
| Last-five-minute temperature | 49.035 C | 37.983 C |
| Fan duty / mean physical RPM | 70% / 2,157.114 | 50% / 1,678.099 |
| Mean / last-five-minute graphics clock | 1,031.357 / 1,029.869 MHz | 180.250 / 180.366 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.650 seconds mean
request duration. Its closing minute medians were 49/49/49/49/49 C. All
quality and cleanup gates passed with zero thermal or brake activity.

Running this cell first in R3 completed the Latin order rotation. Relative to
30%, it reduced the loaded-card mean temperature by 4.557 C and the idle-top
neighbor by 4.375 C. Relative to 50%, the extra approximately 479 RPM bought
0.956 C locally and 0.907 C at the neighbor but reduced mean graphics clock by
9.954 MHz and increased mean request duration by 0.130 seconds.
