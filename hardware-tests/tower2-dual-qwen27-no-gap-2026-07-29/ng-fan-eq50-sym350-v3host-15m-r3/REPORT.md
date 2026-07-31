# 350/350 W EQ50 fixed-fan measured run R3

- Run: `2026-07-31T11:08:19Z-ng-fan-eq50-sym350-v3host-15m-r3`
- Cell: `NG-FAN-EQ50-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 50%, GPU1/top 50%
- Result: **pass; internally admissible replicate 3 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.992 W | 349.993 W |
| Mean / last-5m / maximum temperature | 55.332 / 56.027 / 58 C | 70.714 / 72.053 / 75 C |
| Fan / mean RPM | 50% / 1,678.133 | 50% / 1,678.145 |
| Mean / last-5m graphics clock | 1,359.736 / 1,355.281 MHz | 1,230.092 / 1,216.469 MHz |
| Requests/s | 1.3511 | 1.2800 |
| Mean request duration | 23.234 s | 24.699 s |

Both GPUs held 100% utilization and passed all quality gates with zero thermal
or hardware-power-brake events. This was sequence 2 of 3 in Latin-order block
R3 and provides the equal-allocation reference for both directional policies.
