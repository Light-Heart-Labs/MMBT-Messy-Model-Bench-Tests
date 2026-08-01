# 400/400 W 120-point static fixed-fan study at n=2

Two independently initialized 15-minute blocks completed with rotated order:

- R1: EQ60, B70T50, B50T70
- R2: B70T50, B50T70, EQ60

All six cells passed isolation, saturated-power, fan/RPM tracking,
independent-clock, completeness, steady-state, and slowdown-counter gates.
Each GPU averaged approximately 400 W at 100% utilization, and no thermal or
hardware-power-brake event occurred.

| Policy | Top mean temp | Top mean clock | Top mean latency | Bottom mean temp |
|---|---:|---:|---:|---:|
| EQ60 | 76.419 C | 1,530.099 MHz | 22.626 s | 61.131 C |
| B70T50 | 75.812 C | 1,546.238 MHz | 22.549 s | 60.550 C |
| B50T70 | 76.522 C | 1,523.995 MHz | 22.669 s | 61.508 C |

## Paired effects

For B70T50 minus direction-reversed B50T70:

| Response | R1 | R2 | Paired mean | Sample SD |
|---|---:|---:|---:|---:|
| Top mean temperature | -0.567 C | -0.853 C | -0.710 C | 0.202 C |
| Top mean clock | +19.177 MHz | +25.309 MHz | +22.243 MHz | 4.336 MHz |
| Top mean latency | -0.108 s | -0.133 s | -0.121 s | 0.018 s |
| Bottom mean temperature | -0.899 C | -1.018 C | -0.959 C | 0.084 C |
| Top last-5m temperature | -0.961 C | -0.980 C | -0.971 C | 0.013 C |
| Top last-5m clock | +23.610 MHz | +24.420 MHz | +24.015 MHz | 0.573 MHz |

R2 independently reproduces every principal R1 direction. With identical
total commanded fan duty and near-identical total RPM, allocating more fan to
the lower card improves both card temperatures and improves upper-card clock
and latency even though the upper card receives less local fan. This is strong
evidence for shared-flow/lower-card assistance in the no-gap stack.

The result remains preliminary at `n=2/3`; R3 completes the Latin-order
rotation and is required before confidence intervals or a validated 400 W
controller coefficient are published.

Artifacts:

- [`400w-static-fan-120point-observations-n2.csv`](400w-static-fan-120point-observations-n2.csv)
- [`400w-static-fan-120point-effects-n2.csv`](400w-static-fan-120point-effects-n2.csv)
- [`400w-static-fan-120point-n2.png`](400w-static-fan-120point-n2.png)
