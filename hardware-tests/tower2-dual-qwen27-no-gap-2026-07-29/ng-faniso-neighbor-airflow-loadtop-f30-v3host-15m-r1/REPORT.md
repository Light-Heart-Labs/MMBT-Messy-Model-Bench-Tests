# Lower-neighbor fan assistance at 30% - replicate 1

- Source run: `2026-07-31T02-29-37Z-ng-faniso-neighbor-airflow-loadtop-f30-v3host-15m-r1`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F30-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 1, sequence 1 of 3
- Measured window: 900 seconds after 120 seconds loaded warmup
- Result: **pass; internally admissible, n=1/3**

| Metric | GPU0 / bottom idle neighbor | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 19.240 W | 299.993 W |
| Mean / maximum temperature | 26.016 / 27 C | 54.909 / 58 C |
| Last-five-minute temperature | 26.000 C | 55.237 C |
| Fan duty / mean physical RPM | 30% / 1,200.036 | 50% / 1,678.123 |
| Mean / last-five-minute graphics clock | 180.338 / 180.425 MHz | 1,030.668 / 1,027.280 MHz |
| GPU utilization | 0% | 100% |

GPU1 completed 1,056 requests at 1.1733 requests/s with 27.268 seconds
mean request duration. All quality and cleanup gates passed with zero thermal
or brake activity. This is the low-assistance baseline in the first
order-rotated lower-neighbor fan block.
