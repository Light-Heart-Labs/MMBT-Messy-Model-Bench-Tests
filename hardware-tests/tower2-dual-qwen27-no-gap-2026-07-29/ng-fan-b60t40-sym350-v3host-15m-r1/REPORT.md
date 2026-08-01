# 350/350 W B60T40 fixed-fan measured run R1

- Run: `2026-07-31T08:08:35Z-ng-fan-b60t40-sym350-v3host-15m-r1`
- Cell: `NG-FAN-B60T40-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 60%, GPU1/top 40%
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.992 W | 349.992 W |
| Mean / last-5m / maximum temperature | 54.597 / 55.042 / 58 C | 69.895 / 71.060 / 74 C |
| Fan / mean RPM | 60% / 1,917.125 | 40% / 1,439.108 |
| Mean / last-5m graphics clock | 1,355.779 / 1,350.200 MHz | 1,242.258 / 1,227.980 MHz |
| Requests/s | 1.3511 | 1.2800 |
| Mean request duration | 23.293 s | 24.551 s |

Both GPUs held 100% utilization and reached the fixed-fan quantized
steady-state plateau. Primary and independent NVML clocks agreed, workload
accounting matched, fan targets tracked exactly, and all sampled thermal and
hardware-power-brake events and counter deltas were zero. Cleanup restored
automatic fan control, 600 W limits, production containers, and user services.

Relative to R1 EQ50, lower-biased airflow reduced the top mean / last-five-
minute temperature by 1.298 / 1.862 C and raised its mean / last-five-minute
clock by 11.501 / 13.758 MHz. The bottom was 0.874 C cooler but averaged
6.747 MHz lower. These are within-block exploratory differences until all
three order-balanced blocks are complete.
