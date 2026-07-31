# 350/350 W static fixed-fan study at n=2

Two independently initialized 15-minute blocks have completed with rotated
policy order:

- R1: EQ50, B60T40, B40T60
- R2: B60T40, B40T60, EQ50

All six cells passed cold-start, workload-isolation, saturated-power,
fan-tracking, physical-RPM, independent-clock, completeness, steady-state,
and slowdown-counter gates. Each GPU averaged approximately 349.99 W at 100%
utilization, and no thermal or hardware-brake event occurred.

| Policy | Top mean temp | Top mean clock | Top mean latency | Bottom mean temp |
|---|---:|---:|---:|---:|
| EQ50 | 70.947 C | 1,230.866 MHz | 24.662 s | 55.405 C |
| B60T40 | 69.928 C | 1,242.216 MHz | 24.555 s | 54.554 C |
| B40T60 | 70.596 C | 1,228.268 MHz | 24.683 s | 55.471 C |

## Paired effects

For B60T40 minus direction-reversed B40T60:

| Response | R1 | R2 | Paired mean | Sample SD |
|---|---:|---:|---:|---:|
| Top mean temperature | -0.678 C | -0.658 C | -0.668 C | 0.014 C |
| Top mean clock | +16.074 MHz | +11.823 MHz | +13.949 MHz | 3.006 MHz |
| Top mean latency | -0.169 s | -0.086 s | -0.128 s | 0.059 s |
| Bottom mean temperature | -0.858 C | -0.976 C | -0.917 C | 0.083 C |
| Top last-5m temperature | -0.988 C | -0.388 C | -0.688 C | 0.424 C |
| Top last-5m clock | +18.086 MHz | +11.458 MHz | +14.772 MHz | 4.687 MHz |

The top mean-temperature effect is exceptionally consistent across the first
two order positions, while clock and latency retain the same favorable
direction. At equal total commanded fan duty, allocating more airflow to the
bottom card improves both cards thermally and improves top-card performance.
This supports a shared-flow/pressure mechanism rather than independent local
cooling.

The result remains preliminary at `n=2/3`; a confidence interval or validated
350 W controller coefficient will not be published until R3 completes the
Latin-order rotation.

Artifacts:

- [`350w-static-fan-observations-n2.csv`](350w-static-fan-observations-n2.csv)
- [`350w-static-fan-effects-n2.csv`](350w-static-fan-effects-n2.csv)
- [`350w-static-fan-n2.png`](350w-static-fan-n2.png)
