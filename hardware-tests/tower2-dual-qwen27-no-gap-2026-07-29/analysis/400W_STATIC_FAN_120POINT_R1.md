# 400/400 W 120-point static fixed-fan block R1

The first pre-registered 15-minute block completed in the order EQ60,
B70T50, B50T70. Every cell passed cold-start, isolation, power saturation,
fan/RPM tracking, independent clock, completeness, steady-state, and counter
gates.

| Policy | Bottom / top RPM | Bottom last-5m temp / clock | Top last-5m temp / clock | Bottom / top mean latency |
|---|---:|---:|---:|---:|
| EQ60 | 1,917.1 / 1,917.1 | 61.310 C / 1,759.0 MHz | 77.428 C / 1,514.4 MHz | 21.588 / 22.578 s |
| B70T50 | 2,157.1 / 1,678.1 | 61.003 C / 1,751.8 MHz | 77.027 C / 1,528.1 MHz | 21.599 / 22.539 s |
| B50T70 | 1,678.1 / 2,157.1 | 62.047 C / 1,758.2 MHz | 77.988 C / 1,504.5 MHz | 21.562 / 22.647 s |

At equal total fan command, B70T50 beat direction-reversed B50T70 on the top
card by 0.567 C and 19.177 MHz on full-window means, and by 0.961 C and
23.610 MHz over the final five minutes. Top mean request duration improved by
0.108 seconds. The result is consistent with validated lower-card assistance:
stronger lower-card airflow appears to increase useful flow through the
shared no-gap stack even when the top card receives less local fan duty.

This remains `n=1/3`, and B50T70 ran last. Session drift and execution order
remain plausible contributors, so R2/R3 must rotate the policy order before
the 400 W coefficient is used in controller or 4x-stack forecasts.

Artifacts:

- [`400w-static-fan-120point-r1.csv`](400w-static-fan-120point-r1.csv)
- [`400w-static-fan-120point-r1.png`](400w-static-fan-120point-r1.png)
- [`../static-fan-power-sym400-fan120-measure-r1/`](../static-fan-power-sym400-fan120-measure-r1/)
