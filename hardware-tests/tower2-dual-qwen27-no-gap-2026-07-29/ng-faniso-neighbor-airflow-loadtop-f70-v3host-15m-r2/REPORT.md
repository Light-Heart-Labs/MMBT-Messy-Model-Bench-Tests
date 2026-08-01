# Lower-neighbor fan assistance at 70% - replicate 2

- Source run: `2026-07-31T04-11-41Z-ng-faniso-neighbor-airflow-loadtop-f70-v3host-15m-r2`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F70-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 2, sequence 2 of 3
- Result: **pass; internally admissible, n=2/3**

| Metric | GPU0 / bottom idle | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 22.741 W | 299.993 W |
| Mean / maximum temperature | 26.000 / 26 C | 49.882 / 53 C |
| Last-five-minute temperature | 26.000 C | 50.042 C |
| Fan / mean RPM | 70% / 2,157.009 | 50% / 1,678.080 |
| Mean / last-five-minute clock | 180.413 / 180.378 MHz | 1,046.191 / 1,043.400 MHz |

GPU1 completed 1,088 requests at 1.2089 requests/s and 26.830 seconds mean
duration. Relative to 30%, the upper card was 5.033 C cooler and 16.829 MHz
faster for 3.635 W additional lower-card power. All safety counters were zero.
