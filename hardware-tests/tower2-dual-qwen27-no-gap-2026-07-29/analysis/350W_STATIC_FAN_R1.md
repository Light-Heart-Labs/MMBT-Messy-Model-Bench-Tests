# 350/350 W static fixed-fan measured block R1

The first pre-registered 15-minute block completed in the order EQ50,
B60T40, B40T60. Every cell passed its cold-start, workload-isolation,
power-saturation, fan-tracking, independent-clock, completeness,
steady-state, and counter gates.

| Policy | Bottom / top RPM | Bottom last-5m temp / clock | Top last-5m temp / clock | Bottom / top mean latency |
|---|---:|---:|---:|---:|
| EQ50 | 1,678.1 / 1,678.1 | 56.047 C / 1,356.2 MHz | 72.922 C / 1,214.2 MHz | 23.278 / 24.657 s |
| B60T40 | 1,917.1 / 1,439.1 | 55.042 C / 1,350.2 MHz | 71.060 C / 1,228.0 MHz | 23.293 / 24.551 s |
| B40T60 | 1,439.1 / 1,917.1 | 56.050 C / 1,355.5 MHz | 72.048 C / 1,209.9 MHz | 23.219 / 24.720 s |

All six GPU exposures averaged approximately 349.99 W at 100% utilization.
All fixed fan targets tracked exactly, and software-thermal,
hardware-thermal, and hardware-power-brake event samples and counter deltas
were zero.

## Preliminary mechanism signal

At equal total commanded fan duty, B60T40 outperformed the direction-reversed
B40T60 on the top card by 0.988 C and 18.086 MHz over the final five minutes.
It also improved the top relative to equal 50/50 by 1.862 C and 13.758 MHz.
The bottom card was cooler under B60T40 than either alternative. This direction
is consistent with the separately validated idle-lower-neighbor experiment:
bottom-card airflow appears to increase useful flow or pressure through the
shared no-gap stack, so local top-fan duty is not an adequate proxy for top
cooling.

This is still `n=1/3`. Because the favorable policy ran second, thermal
history, execution order, and session drift remain plausible contributors.
R2 runs B60T40, B40T60, EQ50; R3 runs B40T60, EQ50, B60T40. Only their paired,
order-balanced aggregate may be used for the 350 W fan-allocation coefficient
or controller design.

Artifacts:

- [`350w-static-fan-r1.csv`](350w-static-fan-r1.csv)
- [`350w-static-fan-r1.png`](350w-static-fan-r1.png)
