# Lower-neighbor fan assistance at 30% - replicate 2

- Source run: `2026-07-31T04-36-14Z-ng-faniso-neighbor-airflow-loadtop-f30-v3host-15m-r2`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F30-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 2, sequence 3 of 3
- Result: **pass; internally admissible, n=2/3**

| Metric | GPU0 / bottom idle | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 19.106 W | 299.993 W |
| Mean / maximum temperature | 26.172 / 27 C | 54.915 / 58 C |
| Last-five-minute temperature | 26.515 C | 55.675 C |
| Fan / mean RPM | 30% / 1,200.029 | 50% / 1,678.132 |
| Mean / last-five-minute clock | 180.418 / 180.486 MHz | 1,029.362 / 1,025.960 MHz |

GPU1 completed 1,056 requests at 1.1733 requests/s and 27.296 seconds mean
duration. All counters were zero except the expected continuous software
power-cap state.
