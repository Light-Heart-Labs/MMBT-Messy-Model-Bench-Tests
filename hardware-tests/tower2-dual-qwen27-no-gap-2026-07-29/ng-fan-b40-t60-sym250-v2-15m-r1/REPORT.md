# Fixed-fan 250/250 W, bottom/top 40/60% - v2 replicate 1

- Run: `2026-07-30T10-50-23Z-ng-fan-b40-t60-sym250-v2-15m-r1`
- Cell: `NG-FAN-B40-T60-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.987 W | 249.994 W |
| Mean / maximum temperature | 46.679 / 49 C | 57.807 / 61 C |
| Last-five-minute mean temperature | 47.032 C | 59.003 C |
| Mean physical fan RPM | 1,439.117 | 1,917.151 |
| Mean graphics clock | 814.587 MHz | 794.945 MHz |
| Last-five-minute mean clock | 813.619 MHz | 792.973 MHz |
| Completed request rate | 0.9956 req/s | 0.8889 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 59, 59, 59, 59, 59 C |

All v2 gates passed with zero slowdown/brake events. Total mean card-level fan
speed was 3,356.268 RPM, within 0.005 RPM of the validated 50/50 policy mean.

This was a prospective check of the frozen v1 piecewise-linear 40/60
prediction. Observed minus predicted errors were +0.141/+0.535 C for
bottom/top temperature and +0.779/+0.732 MHz for bottom/top mean clock. Total
request throughput matched the frozen prediction to rounding (1.8845 observed
versus 1.88445 req/s predicted), although the fixed-window request counts were
redistributed between GPUs.

At the same aggregate fan RPM, 40/60 was hotter on both cards than the
previously validated 60/40 allocation and produced a 19.642 MHz top-minus-
bottom clock deficit. This first replicate is consistent with the hypothesis
that bottom-card airflow assists the entire no-gap stack more effectively than
the same RPM assigned to the top card. Replicates 2 and 3 are required before
promoting that comparison to an internally validated result.
