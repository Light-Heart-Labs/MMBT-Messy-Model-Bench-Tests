# Bottom-card own-fan isolation - internally validated at n=3

Three independently initialized, order-rotated blocks measured the saturated
300 W bottom GPU at fixed 30%, 50%, and 70% fan duty while the model-resident
top GPU remained idle at fixed 50%. All nine 15-minute cells held approximately
300 W and 100% utilization, tracked physical RPM, reached the frozen
temperature plateau, preserved workload isolation, and recorded zero thermal
or power-brake events/counter growth.

This is internally validated for the Tower2 no-gap configuration. It is not
transferable to another chassis or ambient condition because calibrated room,
local-inlet, and inter-card probes were unavailable.

## Validated operating points

| Bottom fan | Loaded mean temp | Loaded last-5m temp | Loaded mean clock | Mean request duration | Idle-top mean temp |
|---:|---:|---:|---:|---:|---:|
| 30% | 55.212 C | 55.642 C | 1,031.233 MHz | 26.713 s | 43.707 C |
| 50% | 52.088 C | 52.400 C | 1,032.333 MHz | 26.653 s | 40.623 C |
| 70% | 50.189 C | 50.375 C | 1,026.651 MHz | 26.758 s | 38.785 C |

Values are means across three runs. The machine-readable summary contains
sample standard deviations and 95% t intervals with the run—not telemetry
sample—as the inference unit.

## Paired block effects

| Contrast | Loaded mean temp | Idle-top mean temp | Loaded mean clock | Mean request duration |
|---|---:|---:|---:|---:|
| 50% minus 30% | -3.124 C | -3.084 C | +1.099 MHz | -0.060 s |
| 70% minus 50% | -1.899 C | -1.838 C | -5.682 MHz | +0.105 s |
| 70% minus 30% | -5.023 C | -4.922 C | -4.582 MHz | +0.045 s |

The 30-to-70% thermal effect is strong and consistent: its paired 95% interval
is -6.398 to -3.648 C locally and -6.453 to -3.390 C at the idle upper
neighbor. This validates both local cooling and upward propagation of the
lower card's fan-driven airflow.

The 50-versus-30% latency improvement also excludes zero (-0.111 to -0.009 s).
The additional 70-versus-50% cooling has a wide three-run interval that barely
includes zero, while its latency penalty is consistent (+0.044 to +0.166 s).
Clock intervals remain wide because R3 began from a cooler block/session state,
but all three blocks showed 70% slower than 50%.

## Engineering interpretation

At a continuously active 300 W software power cap, 50% is the best observed
performance point and 70% is the best observed thermal-margin point. More
local fan is not free: the 70% condition repeatedly traded a small amount of
clock/latency performance for cooling despite being tens of degrees below the
thermal limit and having no slowdown events. Fan electrical demand competing
inside the board-power budget is consistent with the result, but is not yet
directly measured.

This matters for a cooperative stack controller. A cooler lower GPU can
produce useful upward airflow, but commanding excess fan on a power-capped
card may have a local performance cost. Dynamic assistance therefore needs an
explicit objective and should increase lower-card airflow only when the
downstream thermal/fairness benefit exceeds the local fan-power, noise, and
wear cost. Stock auto, static 50/50, static lower-biased, and dynamic
top/hottest-card-led policies will be compared directly at n=3 before a
controller is promoted.

Artifacts:

- [`observations`](fan-isolation-own-bottom-observations-n3.csv)
- [`summary with uncertainty`](fan-isolation-own-bottom-summary-n3.csv)
- [`paired effects`](fan-isolation-own-bottom-effects-n3.csv)
- [`publication figure`](fan-isolation-own-bottom-n3.png)
- block CSVs: [`R1`](fan-isolation-own-bottom-r1.csv),
  [`R2`](fan-isolation-own-bottom-r2.csv), and
  [`R3`](fan-isolation-own-bottom-r3.csv)
