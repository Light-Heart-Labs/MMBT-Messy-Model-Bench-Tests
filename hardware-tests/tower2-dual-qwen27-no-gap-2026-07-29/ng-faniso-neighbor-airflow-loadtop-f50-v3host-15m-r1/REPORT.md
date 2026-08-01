# Lower-neighbor fan assistance at 50% - replicate 1

- Source run: `2026-07-31T02-53-58Z-ng-faniso-neighbor-airflow-loadtop-f50-v3host-15m-r1`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F50-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 1, sequence 2 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible, n=1/3**

| Metric | GPU0 / bottom idle neighbor | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 20.484 W | 299.993 W |
| Mean / maximum temperature | 25.994 / 26 C | 52.120 / 54 C |
| Last-five-minute temperature | 26.000 C | 52.203 C |
| Fan duty / mean physical RPM | 50% / 1,678.022 | 50% / 1,678.118 |
| Mean / last-five-minute graphics clock | 180.299 / 180.241 MHz | 1,040.423 / 1,038.839 MHz |
| GPU utilization | 0% | 100% |

GPU1 completed 1,056 requests at 1.1733 requests/s with 26.973 seconds
mean request duration. Relative to the 30% lower-neighbor baseline, this cell
reduced top mean temperature by 2.789 C, raised mean clock by 9.755 MHz, and
reduced mean request duration by 0.295 seconds while adding 1.244 W at the
idle lower card. All quality and cleanup gates passed with zero thermal or
brake activity.
