# Lower-neighbor fan assistance at 50% - replicate 3

- Source run: `2026-07-31T05-51-22Z-ng-faniso-neighbor-airflow-loadtop-f50-v3host-15m-r3`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F50-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 3, sequence 3 of 3
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom idle | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 20.613 W | 299.993 W |
| Mean / maximum temperature | 26.000 / 26 C | 51.948 / 55 C |
| Last-five-minute temperature | 26.000 C | 52.052 C |
| Fan / mean RPM | 50% / 1,678.003 | 50% / 1,678.077 |
| Mean / last-five-minute clock | 180.413 / 180.470 MHz | 1,034.538 / 1,033.908 MHz |

GPU1 completed 1,056 requests at 1.1733 requests/s and 27.129 seconds mean
duration. All thermal and hardware power-brake counters were zero. This final
Latin-order block completes the three-replicate comparison.
