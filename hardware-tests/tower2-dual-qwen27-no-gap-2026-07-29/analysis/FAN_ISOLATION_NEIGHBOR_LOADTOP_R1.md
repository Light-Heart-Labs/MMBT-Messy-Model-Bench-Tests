# Lower-neighbor fan assistance with the top GPU loaded - preliminary R1

This first neighbor-airflow block held GPU1/top at 300 W, 100% utilization,
and fixed 50% own fan while GPU0/bottom remained idle and only its fan changed
from 30% to 50% to 70%. All three independently initialized 15-minute cells
passed power, workload-isolation, steady-state, fan/RPM, independent-clock,
event-counter, and cleanup gates.

## Operating points

| Lower fan | Lower RPM | Upper mean / last-5m temp | Upper mean / last-5m clock | Mean request duration | Lower idle power |
|---:|---:|---:|---:|---:|---:|
| 30% | 1,200.036 | 54.909 / 55.237 C | 1,030.668 / 1,027.280 MHz | 27.268 s | 19.240 W |
| 50% | 1,678.022 | 52.120 / 52.203 C | 1,040.423 / 1,038.839 MHz | 26.973 s | 20.484 W |
| 70% | 2,157.073 | 49.824 / 50.038 C | 1,042.998 / 1,042.656 MHz | 26.882 s | 23.157 W |

## Preliminary within-block effects

| Contrast | Upper mean temp | Upper last-5m temp | Upper mean clock | Upper last-5m clock | Mean request duration | Lower idle power |
|---|---:|---:|---:|---:|---:|---:|
| 50% minus 30% | -2.789 C | -3.034 C | +9.755 MHz | +11.559 MHz | -0.295 s | +1.244 W |
| 70% minus 50% | -2.296 C | -2.165 C | +2.575 MHz | +3.817 MHz | -0.091 s | +2.673 W |
| 70% minus 30% | -5.085 C | -5.199 C | +12.330 MHz | +15.376 MHz | -0.386 s | +3.917 W |

This is the cleanest causal evidence yet for cooperative lower-to-upper
airflow. The loaded upper card's board power, utilization, own fan RPM, and
workload were held constant; therefore the extra lower-fan power did not
compete inside the loaded card's 300 W allowance. The direction was monotonic
in temperature, clock, and request latency.

The result is still `n=1/3`. R2 and R3 must rotate the step order before
estimating uncertainty or promoting a control coefficient. If it reproduces,
it directly supports a stack-aware service that commands cooler lower cards
to assist a thermally disadvantaged upper card, particularly in three- and
four-card stacks.

Artifacts:
[`CSV`](fan-isolation-neighbor-loadtop-r1.csv) and
[`figure`](fan-isolation-neighbor-loadtop-r1.png).
