# Lower-neighbor fan assistance at 30% - replicate 3

- Source run: `2026-07-31T05-26-59Z-ng-faniso-neighbor-airflow-loadtop-f30-v3host-15m-r3`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F30-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 3, sequence 2 of 3
- Result: **pass; internally validated at n=3**

| Metric | GPU0 / bottom idle | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 19.096 W | 299.993 W |
| Mean / maximum temperature | 26.003 / 27 C | 54.682 / 58 C |
| Last-five-minute temperature | 26.002 C | 55.048 C |
| Fan / mean RPM | 30% / 1,200.022 | 50% / 1,678.117 |
| Mean / last-five-minute clock | 180.418 / 180.486 MHz | 1,024.556 / 1,023.482 MHz |

GPU1 completed 1,056 requests at 1.1733 requests/s and 27.343 seconds mean
duration. All thermal and hardware power-brake counters were zero. This final
Latin-order block completes the three-replicate comparison.
