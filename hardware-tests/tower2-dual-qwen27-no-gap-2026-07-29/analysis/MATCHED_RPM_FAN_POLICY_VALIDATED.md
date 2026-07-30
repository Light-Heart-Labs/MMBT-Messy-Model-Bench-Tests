# Validated matched-RPM fan-policy result

## Scope

This result applies to Tower2's current adjacent no-gap pair of RTX PRO 6000
Blackwell Workstation Edition cards running identical Qwen3.6-27B AWQ-INT4
workloads at 250/250 W. Each policy has three independently initialized
15-minute steady-state runs. All nine runs passed the prospective v2 plateau,
power, utilization, isolation, physical-fan tracking, and event-counter gates.

The inference unit is the run (`n=3` per policy), not the thousands of
sub-second telemetry samples. Error estimates therefore describe between-run
repeatability rather than pseudoreplicated sensor precision.

## Policy means

Values are mean +/- sample standard deviation across the three runs.

| Bottom/top fan policy | Total physical RPM | Bottom / top temperature | Bottom / top clock | Bottom / top requests/s |
|---|---:|---:|---:|---:|
| 50/50 | 3,356.263 +/- 0.024 | 46.435 +/- 0.129 / 57.722 +/- 0.162 C | 810.574 +/- 1.120 / 796.723 +/- 0.634 MHz | 0.9956 / 0.9244 |
| 70/30 | 3,357.186 +/- 0.017 | 45.470 +/- 0.175 / 56.294 +/- 0.051 C | 804.394 +/- 2.087 / 803.031 +/- 1.103 MHz | 0.9600 / 0.9244 |
| 30/70 | 3,357.224 +/- 0.037 | 46.641 +/- 0.029 / 56.821 +/- 0.210 C | 817.042 +/- 1.052 / 791.704 +/- 1.904 MHz | 0.9600 / 0.8889 |

The largest difference among policy mean total fan speeds is 0.961 RPM, or
0.029%. This is a fan-allocation experiment, not a hidden total-airflow
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

The temperature and clock contrasts are repeatable at this operating point.
The identical request rates across replicates are also operationally
meaningful, but their apparent zero variance must not be treated as
infinite-precision inference: a fixed 900-second window produces quantized
completed-request counts.

## Interpretation

The validated result rejects a purely local fan model. Moving approximately
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
