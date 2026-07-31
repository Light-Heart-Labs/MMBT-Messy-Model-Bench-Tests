# Lower-neighbor fan assistance at 70% - replicate 3

- Source run: `2026-07-31T05-02-50Z-ng-faniso-neighbor-airflow-loadtop-f70-v3host-15m-r3`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F70-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 3, sequence 1 of 3
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom idle | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 23.277 W | 299.993 W |
| Mean / maximum temperature | 25.999 / 26 C | 49.848 / 52 C |
| Last-five-minute temperature | 26.000 C | 50.037 C |
| Fan / mean RPM | 70% / 2,157.043 | 50% / 1,678.097 |
| Mean / last-five-minute clock | 180.268 / 180.366 MHz | 1,040.668 / 1,039.534 MHz |

GPU1 completed 1,056 requests at 1.1733 requests/s and 26.926 seconds mean
duration. All thermal and hardware power-brake counters were zero. This final
Latin-order block completes the three-replicate comparison.
