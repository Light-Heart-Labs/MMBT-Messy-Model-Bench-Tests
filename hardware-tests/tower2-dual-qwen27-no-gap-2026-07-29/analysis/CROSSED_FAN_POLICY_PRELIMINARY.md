# Preliminary crossed-fan policy result

## Result

The first 250/250 W v2 triplet directly tested where a fixed aggregate fan
budget should be placed in the no-gap two-card stack. All cells used the same
Qwen3.6-27B workload, 15-minute measured duration, power caps, cold-soak
protocol, and total commanded fan duty.

| Policy bottom/top | Total RPM | Bottom / top mean temp | Bottom / top mean clock | Bottom / top req/s |
|---|---:|---:|---:|---:|
| 50/50 | 3,356.270 | 46.293 / 57.541 C | 811.635 / 797.396 MHz | 0.9956 / 0.9244 |
| 70/30 | 3,357.205 | 45.311 / 56.259 C | 806.668 / 802.214 MHz | 0.9600 / 0.9244 |
| 30/70 | 3,357.187 | 46.654 / 56.596 C | 818.249 / 790.434 MHz | 0.9600 / 0.8889 |

Physical fan speed makes this an unusually strong actuator comparison. The
70/30 and 30/70 totals differ by only 0.018 RPM; 70/30 differs from 50/50 by
only 0.028%. At essentially fixed aggregate fan RPM, 70/30 is the only policy
that is cooler than 50/50 on both cards. Against the exact reverse allocation,
70/30 is 1.343 C cooler bottom and 0.337 C cooler top.

## What it means

The result rejects a purely local cooling model in which each card benefits
only from its own fans. Cutting the top card from 50% to 30% did not make it
hotter when the bottom card rose from 50% to 70%; the top instead cooled by
1.282 C. The bottom card's fans therefore contribute useful airflow to the top
card in this orientation. The cooler bottom card is not merely rejecting heat:
when given more fan duty it helps carry the shared stack airflow load.

The policy also changes performance distribution. The sum of both mean clocks
is nearly invariant across the triplet (1,608.683 to 1,609.031 MHz), but the
top-minus-bottom clock gap is -4.454 MHz at 70/30 versus -14.239 MHz at 50/50
and -27.815 MHz at 30/70. Bottom-biased fan effort makes the two cards much
more performance-balanced and raises top throughput relative to the reverse
policy.

A plausible additional mechanism is fan electrical power. If fan power is
inside each GPU's reported board-power envelope, high local fan duty consumes
power that could otherwise support compute clocks. Moving fan duty from the
thermally disadvantaged top card to the cooler bottom card would then provide
two benefits: upstream airflow assistance and preservation of top-card compute
power. This campaign does not yet measure fan watts, so the electrical channel
is a testable hypothesis, not a conclusion.

## Limits and next tests

Every policy is currently `n=1/3`, all observations are from one session, and
there are no calibrated room/inlet probes. The result is internally useful and
highly actionable, but not yet a transferable server-design rule.

Priority follow-up:

1. replicate all three policies twice more in randomized order;
2. add 60/40 and 80/20 around the apparent bottom-biased optimum;
3. repeat at 400/400 W and 500/500 W after 250 W validation;
4. measure wall power or fan-rail electrical power to test the board-budget
   mechanism;
5. add local inlet probes below, between, and above cards to separate shared
   airflow from recirculated-air temperature;
6. fit temperature and clock responses against per-card RPM rather than fan
   percentage.

The machine-readable source is
[`crossed-fan-policy-r1.csv`](crossed-fan-policy-r1.csv).
