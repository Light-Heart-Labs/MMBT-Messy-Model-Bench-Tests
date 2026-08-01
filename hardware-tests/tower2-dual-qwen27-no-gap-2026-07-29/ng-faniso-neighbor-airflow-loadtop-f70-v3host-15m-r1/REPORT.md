# Lower-neighbor fan assistance at 70% - replicate 1

- Source run: `2026-07-31T03-18-06Z-ng-faniso-neighbor-airflow-loadtop-f70-v3host-15m-r1`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F70-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 1, sequence 3 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible, n=1/3**

| Metric | GPU0 / bottom idle neighbor | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 23.157 W | 299.993 W |
| Mean / maximum temperature | 26.000 / 26 C | 49.824 / 52 C |
| Last-five-minute temperature | 26.000 C | 50.038 C |
| Fan duty / mean physical RPM | 70% / 2,157.073 | 50% / 1,678.078 |
| Mean / last-five-minute graphics clock | 180.494 / 180.595 MHz | 1,042.998 / 1,042.656 MHz |
| GPU utilization | 0% | 100% |

GPU1 completed 1,088 requests at 1.2089 requests/s with 26.882 seconds
mean request duration. Relative to the 30% lower-neighbor baseline, this cell
reduced top mean temperature by 5.085 C, raised mean clock by 12.330 MHz, and
reduced mean request duration by 0.386 seconds while adding 3.917 W at the
idle lower card. All quality and cleanup gates passed with zero thermal or
brake activity.
