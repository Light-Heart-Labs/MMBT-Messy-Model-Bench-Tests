# Bottom-card own-fan isolation at 50% - replicate 3

- Source run: `2026-07-31T01-35-03Z-ng-faniso-own-saturated-loadbottom-f50-v3host-15m-r3`
- Cell: `NG-FANISO-OWN-LOADBOTTOM-F50-V3HOST-15M`
- Block: own-fan saturated, bottom loaded, replicate 3, sequence 3 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible, n=3/3**

| Metric | GPU0 / bottom loaded | GPU1 / top model-resident idle |
|---|---:|---:|
| Mean board power | 299.994 W | 21.353 W |
| Mean / maximum temperature | 49.868 / 53 C | 38.425 / 39 C |
| Last-five-minute temperature | 50.048 C | 39.000 C |
| Fan duty / mean physical RPM | 50% / 1,678.122 | 50% / 1,678.193 |
| Mean / last-five-minute graphics clock | 1,041.311 / 1,037.913 MHz | 180.425 / 180.468 MHz |
| GPU utilization | 100% | 0% |

GPU0 completed 1,088 requests at 1.2089 requests/s with 26.520 seconds mean
request duration. Its closing minute medians were 50/50/50/50/50 C. All
quality and cleanup gates passed with zero thermal or brake activity.

Within R3, 50% reduced loaded-card mean temperature by 3.601 C and idle-top
temperature by 3.468 C relative to 30%, while reducing mean request duration
by 0.061 seconds. It was 0.956 C warmer than 70% but 9.954 MHz faster and
0.130 seconds lower latency at the same 300 W board cap.
