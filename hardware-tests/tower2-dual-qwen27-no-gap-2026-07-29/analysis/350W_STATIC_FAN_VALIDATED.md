# 350/350 W static fixed-fan study validated at n=3

Three independently initialized 15-minute blocks completed with rotated policy
order. All nine cells held both GPUs at approximately 350 W and 100%
utilization, reached fixed-fan steady state, tracked commanded duty and
physical RPM, passed workload-isolation and independent-clock gates, and
recorded zero software-thermal, hardware-thermal, or power-brake events.

| Policy | Top mean temp | Top mean clock | Top mean latency | Bottom mean temp |
|---|---:|---:|---:|---:|
| EQ50 | 70.869 C | 1,230.608 MHz | 24.674 s | 55.380 C |
| B60T40 | 69.987 C | 1,240.944 MHz | 24.566 s | 54.608 C |
| B40T60 | 70.639 C | 1,226.940 MHz | 24.699 s | 55.511 C |

## Validated paired effects

For lower-biased B60T40 minus direction-reversed B40T60:

| Response | Paired mean | 95% CI |
|---|---:|---:|
| Top mean temperature | -0.652 C | [-0.725, -0.579] C |
| Top mean graphics clock | +14.005 MHz | [+8.719, +19.290] MHz |
| Top mean request duration | -0.133 s | [-0.239, -0.027] s |
| Bottom mean temperature | -0.903 C | [-1.062, -0.744] C |
| Top last-5m graphics clock | +14.408 MHz | [+6.029, +22.788] MHz |

Each replicate independently favored B60T40 for top mean temperature, clock,
and latency. The result is especially informative because total commanded fan
duty is identical and the top card itself receives *less* local fan duty under
B60T40. More bottom-card airflow therefore improves upper-card cooling and
performance in this no-gap geometry. This validates a shared-flow/pressure or
series-assistance effect at 350 W rather than an independent-per-card cooling
model.

B60T40 also beat EQ50 by +10.337 MHz in top mean clock (95% CI +5.959 to
+14.715 MHz) and -0.109 seconds in top latency (95% CI -0.116 to -0.101 s).
Its mean-temperature advantage over EQ50 was -0.882 C, but the small n=3
confidence interval crosses zero [-1.792, +0.027 C]; that contrast should not
be described as thermally conclusive yet.

The bottom clock response moves slightly in the opposite direction and its
confidence interval crosses zero. Fan RPM is therefore not intrinsically
negative for clock: it redistributes cooling benefit through the stack, while
per-card boost remains affected by temperature, silicon/workload variation,
and power-limit scheduling. The robust top-card clock and latency gains are
the controller-relevant result.

This is internally validated for Tower2's current no-gap two-card geometry.
It is not yet transferable to arbitrary chassis or three-/four-card stacks
because calibrated ambient and card-inlet temperatures are unavailable.

Artifacts:

- [`350w-static-fan-observations-n3.csv`](350w-static-fan-observations-n3.csv)
- [`350w-static-fan-effects-n3.csv`](350w-static-fan-effects-n3.csv)
- [`350w-static-fan-policy-summary-n3.csv`](350w-static-fan-policy-summary-n3.csv)
- [`350w-static-fan-validated-n3.png`](350w-static-fan-validated-n3.png)
