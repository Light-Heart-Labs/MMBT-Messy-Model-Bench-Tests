# Lower-neighbor fan assistance at 50% - replicate 2

- Source run: `2026-07-31T03-47-25Z-ng-faniso-neighbor-airflow-loadtop-f50-v3host-15m-r2`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F50-V3HOST-15M`
- Block: neighbor-airflow, top loaded, replicate 2, sequence 1 of 3
- Result: **pass; internally admissible, n=2/3**

| Metric | GPU0 / bottom idle | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 20.218 W | 299.993 W |
| Mean / maximum temperature | 26.000 / 26 C | 52.153 / 55 C |
| Last-five-minute temperature | 26.000 C | 52.894 C |
| Fan / mean RPM | 50% / 1,677.978 | 50% / 1,678.093 |
| Mean / last-five-minute clock | 180.268 / 180.340 MHz | 1,040.874 / 1,038.730 MHz |

GPU1 completed 1,056 requests at 1.1733 requests/s and 27.009 seconds mean
duration. Upper mean temperature reproduced R1 within +0.033 C.
