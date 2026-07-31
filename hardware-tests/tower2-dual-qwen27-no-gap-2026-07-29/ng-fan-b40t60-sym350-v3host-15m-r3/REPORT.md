# 350/350 W B40T60 fixed-fan measured run R3

- Run: `2026-07-31T10:39:13Z-ng-fan-b40t60-sym350-v3host-15m-r3`
- Cell: `NG-FAN-B40T60-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 40%, GPU1/top 60%
- Result: **pass; internally admissible replicate 3 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.993 W | 349.992 W |
| Mean / last-5m / maximum temperature | 55.591 / 56.043 / 59 C | 70.726 / 72.040 / 74 C |
| Fan / mean RPM | 40% / 1,439.120 | 60% / 1,917.134 |
| Mean / last-5m graphics clock | 1,364.316 / 1,358.810 MHz | 1,224.284 / 1,211.938 MHz |
| Requests/s | 1.3867 | 1.2800 |
| Mean request duration | 23.226 s | 24.731 s |

Both GPUs held 100% utilization and passed saturated-power, steady-state,
workload-isolation, fan/RPM tracking, independent-clock, completeness, and
counter gates. Thermal and hardware-power-brake events and counter deltas were
zero. This was sequence 1 of 3 in Latin-order block R3.
