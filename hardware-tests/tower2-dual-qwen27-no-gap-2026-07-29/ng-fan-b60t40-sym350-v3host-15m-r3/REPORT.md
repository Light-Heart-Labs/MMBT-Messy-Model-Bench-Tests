# 350/350 W B60T40 fixed-fan measured run R3

- Run: `2026-07-31T11:36:27Z-ng-fan-b60t40-sym350-v3host-15m-r3`
- Cell: `NG-FAN-B60T40-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 60%, GPU1/top 40%
- Result: **pass; internally admissible replicate 3 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.993 W | 349.992 W |
| Mean / last-5m / maximum temperature | 54.717 / 55.070 / 58 C | 70.106 / 71.505 / 74 C |
| Fan / mean RPM | 60% / 1,917.138 | 40% / 1,439.102 |
| Mean / last-5m graphics clock | 1,356.894 / 1,351.755 MHz | 1,238.401 / 1,225.619 MHz |
| Requests/s | 1.3867 | 1.2800 |
| Mean request duration | 23.274 s | 24.587 s |

Both GPUs held 100% utilization and passed every quality gate with zero
thermal or hardware-power-brake events. Against the reversed B40T60 policy in
the same block, B60T40 reduced top mean temperature by 0.620 C, raised its
mean clock by 14.117 MHz, and reduced mean request duration by 0.144 seconds.
This was sequence 3 of 3 in Latin-order block R3.
