# Lower-neighbor 30% fan / top-loaded 300 W qualification

- Source run: `2026-07-31T02-17-16Z-ng-faniso-neighbor-loadtop-f30-p300-v3host-bump-r1`
- Cell: `NG-FANISO-NEIGHBOR-LOADTOP-F30-P300-V3HOST-BUMP`
- Measured window: 120 seconds after 120 seconds loaded warmup
- Result: **qualification pass; safety-only and non-inferential**

| Metric | GPU0 / bottom idle neighbor | GPU1 / top loaded |
|---|---:|---:|
| Mean board power | 19.124 W | 299.992 W |
| Mean / maximum temperature | 26.000 / 26 C | 52.782 / 55 C |
| Fan duty / mean physical RPM | 30% / 1,199.955 | 50% / 1,678.686 |
| Mean graphics clock | 180.573 MHz | 1,037.119 MHz |
| GPU utilization | 0% | 100% |

The upper GPU completed 160 measured requests at 1.3333 requests/s with
27.056 seconds mean request duration. Both fan banks tracked their targets,
the top card held the 300 W cap continuously, the bottom card remained idle,
and all thermal, power-brake, isolation, telemetry, and cleanup gates passed.

The top temperature slope remained +1.4956 C/min during the intentionally
short window, so this bump is not a steady-state replicate and cannot estimate
neighbor-fan benefit. It qualifies the lowest planned lower-fan condition for
the 15-minute neighbor-airflow blocks.
