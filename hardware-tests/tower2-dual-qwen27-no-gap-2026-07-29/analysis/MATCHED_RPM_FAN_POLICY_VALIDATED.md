# Validated matched-RPM fan-policy result

## Scope

This result applies to Tower2's current adjacent no-gap pair of RTX PRO 6000
Blackwell Workstation Edition cards running identical Qwen3.6-27B AWQ-INT4
workloads at 250/250 W. Each policy has three independently initialized
15-minute steady-state runs. All 15 runs across five policies passed the prospective v2 plateau,
power, utilization, isolation, physical-fan tracking, and event-counter gates.

The inference unit is the run (`n=3` per policy), not the thousands of
sub-second telemetry samples. Error estimates therefore describe between-run
repeatability rather than pseudoreplicated sensor precision.

## Policy means

Values are mean +/- sample standard deviation across the three runs.

| Bottom/top fan policy | Total physical RPM | Bottom / top temperature | Bottom / top clock | Bottom / top requests/s |
|---|---:|---:|---:|---:|
| 30/70 | 3,357.224 +/- 0.037 | 46.641 +/- 0.029 / 56.821 +/- 0.210 C | 817.042 +/- 1.052 / 791.704 +/- 1.904 MHz | 0.9600 / 0.8889 |
| 40/60 | 3,356.243 +/- 0.034 | 46.694 +/- 0.014 / 57.856 +/- 0.050 C | 814.472 +/- 0.099 / 795.645 +/- 0.726 MHz | 0.9952 / 0.9007 |
| 50/50 | 3,356.263 +/- 0.024 | 46.435 +/- 0.129 / 57.722 +/- 0.162 C | 810.574 +/- 1.120 / 796.723 +/- 0.634 MHz | 0.9956 / 0.9244 |
| 60/40 | 3,356.226 +/- 0.020 | 45.973 +/- 0.120 / 57.285 +/- 0.033 C | 808.742 +/- 0.950 / 800.729 +/- 0.490 MHz | 0.9956 / 0.9244 |
| 70/30 | 3,357.186 +/- 0.017 | 45.470 +/- 0.175 / 56.294 +/- 0.051 C | 804.394 +/- 2.087 / 803.031 +/- 1.103 MHz | 0.9600 / 0.9244 |

The largest difference among policy mean total fan speeds is 0.998 RPM, or
0.030%. This is a fan-allocation experiment, not a hidden total-airflow
experiment.

## Paired run-block effects

The table reports 70/30 minus the reference policy. Confidence intervals use
the three replicate-block differences and a two-sided Student-t interval with
two degrees of freedom.

| Response | Versus 50/50, mean difference (95% CI) | Versus 30/70, mean difference (95% CI) |
|---|---:|---:|
| Bottom temperature | -0.965 C (-1.146, -0.784) | -1.171 C (-1.593, -0.748) |
| Top temperature | -1.428 C (-1.741, -1.114) | -0.527 C (-0.946, -0.108) |
| Bottom clock | -6.180 MHz (-10.395, -1.965) | -12.648 MHz (-15.353, -9.942) |
| Top clock | +6.308 MHz (+2.776, +9.840) | +11.327 MHz (+9.317, +13.337) |
| Top-minus-bottom clock gap | +12.488 MHz (+6.393, +18.583) | +23.975 MHz (+20.521, +27.428) |
| Sum of card clocks | +0.128 MHz (-4.702, +4.958) | -1.321 MHz (-4.606, +1.965) |
| Top completed request rate | 0.0000 requests/s | +0.0355 requests/s |

The newly validated midpoint reversal gives an especially direct test because
60/40 and 40/60 use equal and opposite allocations around 50/50:

| Response | 60/40 minus 40/60, mean difference (95% CI) |
|---|---:|
| Total card-level fan RPM | -0.017 RPM (-0.122, +0.088) |
| Bottom temperature | -0.721 C (-0.997, -0.445) |
| Top temperature | -0.570 C (-0.749, -0.392) |
| Bottom clock | -5.730 MHz (-8.258, -3.202) |
| Top clock | +5.084 MHz (+2.063, +8.104) |
| Top-minus-bottom clock gap | +10.814 MHz (+5.298, +16.330) |
| Sum of card clocks | -0.646 MHz (-1.419, +0.126) |

The temperature and clock contrasts are repeatable at this operating point.
The identical request rates across replicates are also operationally
meaningful, but their apparent zero variance must not be treated as
infinite-precision inference: a fixed 900-second window produces quantized
completed-request counts.

## Interpretation

The five-policy response rejects a purely local fan model. Moving approximately
957 RPM of fan speed from the top card to the bottom card, while holding the
total constant, cools the bottom card by 1.17 C **and the top card by 0.53 C**.
The bottom card's fans therefore make a measurable positive contribution to
the top card's thermal condition in this orientation.

The result directly supports the cooperative-airflow hypothesis: the cooler
bottom card is not just a heat source receiving a free ride from the top
card's fan effort. Increasing bottom-card fan effort helps propel the shared
stack flow and can cool the disadvantaged top card more effectively than
spending the same RPM locally on the top card.

Fan placement also redistributes performance. Total mean graphics clock is
nearly invariant among policies, while the top-minus-bottom gap changes from
-25.34 MHz at 30/70 to -1.36 MHz at 70/30. The bottom-biased policy gives up
some bottom clock and transfers almost the same aggregate clock opportunity to
the top card, producing a much more balanced pair. Its top request rate is
4.0% higher than the reverse allocation (0.9244 versus 0.8889 requests/s).

A second mechanism remains plausible but unproven: if fan electrical power is
included inside each card's 250 W board-power limit, moving high fan duty to
the bottom card may preserve compute power on the top card. Fan-rail or
card-component power is not measured, so the present experiment identifies a
policy effect and cross-card airflow contribution but cannot partition
aerodynamic and electrical causes.

## Design guidance supported now

For this exact two-card no-gap configuration at 250/250 W and a total fan
budget near 3,357 card-level RPM, 70% bottom / 30% top is preferred when the
objective is to minimize both card temperatures while balancing performance.
Equal 50/50 maximizes observed aggregate completed-request rate because its
bottom request counter is higher, but it is hotter on both cards and less
clock-balanced. The correct production objective therefore needs to state
whether it values aggregate throughput, top-card fairness, temperature,
acoustics, or fan energy.

This is not yet a universal recommendation for other powers, chassis,
orientations, or three-/four-card stacks. Transferable guidance requires
calibrated ambient and local-inlet probes, fan electrical power, and replicated
fan-allocation cells at higher power.

## Machine-readable evidence

- [`matched-rpm-policy-observations-n3.csv`](matched-rpm-policy-observations-n3.csv):
  one row per independent run.
- [`matched-rpm-policy-summary-n3.csv`](matched-rpm-policy-summary-n3.csv):
  policy means, sample SDs, and run-level 95% intervals.
- [`matched-rpm-policy-effects-n3.csv`](matched-rpm-policy-effects-n3.csv):
  paired replicate-block contrasts and intervals.
- [`matched-rpm-policy-n3.png`](matched-rpm-policy-n3.png): publication figure.
- [`analyze-matched-rpm-policy.py`](analyze-matched-rpm-policy.py):
  reproducible analysis and rendering source.
- [`fan-allocation-response-v1.json`](fan-allocation-response-v1.json):
  bounded, machine-readable 30–70% bottom-fan interpolator with explicit
  extrapolation prohibitions.
- [`fan-allocation-predictions-v1.csv`](fan-allocation-predictions-v1.csv):
  five-percentage-point interpolation grid for planning validation cells.
- [`build-fan-allocation-model.py`](build-fan-allocation-model.py):
  reproducible model builder.
- [`fan-allocation-response-v3.json`](fan-allocation-response-v3.json):
  bounded model containing all five directly observed `n=3` knots.
- [`fan-allocation-v2-validation-at-40-n3.csv`](fan-allocation-v2-validation-at-40-n3.csv):
  immutable-v2 prediction compared with the subsequent 40/60 observations.
- [`build-fan-allocation-model-v3.py`](build-fan-allocation-model-v3.py):
  reproducible promotion of the validated 40/60 knot without altering v1/v2.

## Prospective interpolation check

After v1 was committed, the previously unobserved 60/40 policy was run three
times under the same protocol. It averaged 45.973/57.285 C versus
45.953/57.008 C predicted, an observed-minus-predicted error of only
+0.020/+0.277 C. This validates useful local interpolation accuracy at one
held-out policy; it does not validate other powers or stack sizes.

Clock errors were +1.258/+0.852 MHz. Completed-request interpolation did not
behave continuously: v1 predicted 1.9022 total requests/s, while every 60/40
replicate delivered 1.9200. Fixed-window completed counts form discrete steps,
so v2 retains request data but explicitly prohibits treating its interpolated
request rates as a smooth performance law.

The immutable v1 prediction and comparison are preserved in
[`fan-allocation-v1-validation-at-60-n3.csv`](fan-allocation-v1-validation-at-60-n3.csv).
The updated [`v2 model`](fan-allocation-response-v2.json) promotes 60/40 to a
directly observed `n=3` knot.

The next held-out policy was 40/60. Across three runs it averaged
46.694/57.856 C versus 46.538/57.272 C predicted by immutable v2, errors of
only +0.156/+0.584 C. Clock errors were +0.664/+1.432 MHz. This is a second
successful local temperature interpolation check at the same 250/250 W
condition; it still provides no evidence for extrapolation across power or
stack size. The updated [`v3 model`](fan-allocation-response-v3.json) promotes
40/60 to the fifth directly observed knot.
