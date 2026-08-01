# 350/350 W EQ50 fixed-fan measured run R2

- Run: `2026-07-31T10:05:37Z-ng-fan-eq50-sym350-v3host-15m-r2`
- Cell: `NG-FAN-EQ50-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 50%, GPU1/top 50%
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.992 W | 349.992 W |
| Mean / last-5m / maximum temperature | 55.338 / 55.923 / 58 C | 70.701 / 72.045 / 75 C |
| Fan / mean RPM | 50% / 1,678.143 | 50% / 1,678.123 |
| Mean / last-5m graphics clock | 1,358.261 / 1,357.492 MHz | 1,230.974 / 1,216.649 MHz |
| Requests/s | 1.3867 | 1.2800 |
| Mean request duration | 23.244 s | 24.667 s |

Both GPUs held 100% utilization, reached steady state, and passed workload,
telemetry, fan, independent-clock, power, and counter gates. All thermal and
hardware-power-brake events and counter deltas were zero. Cleanup restored
automatic fan control, 600 W limits, production containers, and services.

Running EQ50 last in R2 rather than first in R1 changed top mean temperature
by -0.492 C but mean clock by only +0.217 MHz. This shows why block pairing
and order balance are needed: quantized temperature can shift modestly while
the performance response remains highly repeatable.
