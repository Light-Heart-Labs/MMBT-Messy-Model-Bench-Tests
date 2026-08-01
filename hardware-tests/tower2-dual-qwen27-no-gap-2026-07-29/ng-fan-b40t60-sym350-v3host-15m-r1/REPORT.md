# 350/350 W B40T60 fixed-fan measured run R1

- Run: `2026-07-31T08:36:19Z-ng-fan-b40t60-sym350-v3host-15m-r1`
- Cell: `NG-FAN-B40T60-SYM350-V3HOST-15M`
- Policy: GPU0/bottom 40%, GPU1/top 60%
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 349.994 W | 349.992 W |
| Mean / last-5m / maximum temperature | 55.455 / 56.050 / 59 C | 70.573 / 72.048 / 75 C |
| Fan / mean RPM | 40% / 1,439.124 | 60% / 1,917.140 |
| Mean / last-5m graphics clock | 1,363.635 / 1,355.544 MHz | 1,226.184 / 1,209.894 MHz |
| Requests/s | 1.3867 | 1.2800 |
| Mean request duration | 23.219 s | 24.720 s |

Both GPUs held 100% utilization and reached the fixed-fan quantized
steady-state plateau. Primary and independent NVML clocks agreed, workload
accounting matched, fan targets tracked exactly, and all sampled thermal and
hardware-power-brake events and counter deltas were zero. Cleanup restored
automatic fan control, 600 W limits, production containers, and user services.

Despite receiving 60% local fan, the top card ran 0.988 C hotter and
18.086 MHz lower in the last five minutes than under B60T40, which instead
gave the bottom card 60%. This within-R1 direction supports a shared,
upstream-assisted airflow path; the result remains preliminary until R2 and
R3 control execution-order and session drift.
