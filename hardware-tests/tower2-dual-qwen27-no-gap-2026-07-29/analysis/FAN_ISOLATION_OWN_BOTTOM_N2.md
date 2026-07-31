# Bottom-card own-fan isolation - two-block replication

Two independently initialized Latin-order blocks now cover the saturated 300 W
bottom-card own-fan conditions:

- R1 order: 30/50/70%
- R2 order: 50/70/30%
- Planned R3 order: 70/30/50%

Every one of the six 15-minute cells held approximately 300 W and 100%
utilization, tracked its physical fan target, reached the frozen temperature
plateau, preserved workload isolation, and recorded zero thermal or brake
events/counter growth. Each fan setting is now `n=2/3`, so the results are
replicated but not yet campaign-validated.

## Two-replicate operating points

| Bottom fan | Mean loaded temp | Mean last-5m temp | Mean loaded clock | Mean last-5m clock | Mean request duration | Mean idle-top temp |
|---:|---:|---:|---:|---:|---:|---:|
| 30% | 56.083 C | 56.453 C | 1,026.543 MHz | 1,024.008 MHz | 26.779 s | 44.614 C |
| 50% | 53.198 C | 53.576 C | 1,027.844 MHz | 1,024.665 MHz | 26.719 s | 41.722 C |
| 70% | 50.827 C | 51.045 C | 1,024.298 MHz | 1,021.148 MHz | 26.812 s | 39.419 C |

## What has replicated

The thermal response is monotonic in both blocks. Relative to 30%, 70% reduced
loaded-card mean temperature by 5.635 C in R1 and 4.877 C in R2. It reduced the
idle top neighbor by 5.590 C and 4.800 C. Moving the 30% condition from first
to last therefore did not remove either the local or neighbor-cooling effect.

The 70-versus-50 performance direction also reproduced unusually closely:

| 70% minus 50% response | R1 | R2 |
|---|---:|---:|
| Loaded mean temperature | -2.523 C | -2.219 C |
| Loaded last-5m temperature | -2.514 C | -2.548 C |
| Loaded mean clock | -3.548 MHz | -3.543 MHz |
| Loaded last-5m clock | -4.209 MHz | -2.824 MHz |
| Mean request duration | +0.105 s | +0.081 s |

Thus, an additional approximately 479 RPM above 50% bought another 2.2-2.5 C
of cooling but did not buy performance at the fixed 300 W board cap. It
repeatedly produced slightly lower clocks and slightly longer request duration
while remaining more than 39 C below the reported temperature limit and
showing no thermal slowdown. This is consistent with fan electrical power or
another board-power/boost-control interaction, not thermal throttling.

The 30-versus-50 clock direction did **not** reproduce: 50% was 3.049 MHz
faster in R1 but 0.447 MHz slower in R2. Consequently, the performance-optimal
fan point cannot yet be called 30% or 50%. The defensible n=2 result is narrower:
70% maximizes thermal margin, while 50% outperformed 70% in both blocks by a
small amount.

R3 completes the Latin rotation and the required `n=3`. Only after R3 should
the campaign estimate mean fan-response coefficients, confidence intervals,
and an optimal-control policy.

Machine-readable sources:
[`fan-isolation-own-bottom-r1.csv`](fan-isolation-own-bottom-r1.csv),
[`fan-isolation-own-bottom-r2.csv`](fan-isolation-own-bottom-r2.csv), and
[`fan-isolation-own-bottom-effects-n2.csv`](fan-isolation-own-bottom-effects-n2.csv).
Block figures:
[`R1`](fan-isolation-own-bottom-r1.png) and
[`R2`](fan-isolation-own-bottom-r2.png).
