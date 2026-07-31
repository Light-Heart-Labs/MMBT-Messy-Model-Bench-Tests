# Static fixed-fan symmetric power spine

## Purpose

This prospective protocol extends the validated 200, 250, and 300 W fixed-fan
work into the missing power dimension. It estimates how the benefit or penalty
of fan allocation changes with GPU heat load while preserving the same
no-gap geometry, dense Qwen workload, telemetry, and quality gates.

The first new anchor is 350/350 W. It fills the interval immediately above the
validated 300 W V3HOST crossover without jumping to the nonlinear high-power
boundary. Three constant-total-commanded-duty policies are tested:

| Policy | Bottom fan | Top fan | Total duty |
|---|---:|---:|---:|
| EQ50 | 50% | 50% | 100 percentage points |
| B60T40 | 60% | 40% | 100 percentage points |
| B40T60 | 40% | 60% | 100 percentage points |

The equal policy identifies the symmetric reference. The crossed policies
measure allocation direction at the same total commanded duty and bracket the
validated 300 W comparison. Physical RPM, not duty alone, remains the measured
airflow proxy.

## Qualification

Every policy at a new power level is a new power/fan combination and receives
a non-inferential two-minute measured bump before any 15-minute cell. For the
350 W qualification block, use the conservative order:

1. EQ50;
2. B40T60, which gives the downstream/top card 60%; and
3. B60T40, which gives the downstream/top card 40%.

Each bump uses:

- 120 seconds warmup, 120 seconds measured, and 60 seconds cooldown;
- 350 W cap and at least 333 W warmup mean on both GPUs;
- 32 identical Qwen requests per GPU;
- 85 C independent emergency cutoff;
- fixed-fan target and physical-RPM tracking;
- 250 ms primary telemetry and an independent jittered NVML clock stream;
- frozen V3HOST preflight and production-workload isolation;
- zero sampled or counter-delta thermal/hardware-brake events; and
- automatic fan-control, power-limit, container, and user-service restoration
  on every exit path.

A bump is safety evidence only. It does not count toward `n` and does not prove
steady state. Failure stops the block; later policies and all 15-minute cells
remain prohibited until the failure is understood.

## Measured design

After all three bumps pass, run three independently initialized 15-minute
blocks with Latin-order rotation:

| Block | Sequence |
|---:|---|
| R1 | EQ50, B60T40, B40T60 |
| R2 | B60T40, B40T60, EQ50 |
| R3 | B40T60, EQ50, B60T40 |

Every cell must pass the fixed-quantized steady-state protocol, workload
isolation, power, fan/RPM, independent-clock, telemetry-completeness, and event
counter gates. Telemetry samples are repeated observations inside a run, not
independent replicates. The three block-level observations provide `n=3`.

Primary paired contrasts are B60T40 minus B40T60 and each crossed policy minus
EQ50 for:

- per-position mean and last-five-minute temperature;
- maximum temperature and thermal-limit margin;
- mean and last-five-minute graphics clock;
- request duration, requests/s, and aggregate throughput;
- per-card physical RPM and total RPM integral;
- temperature and clock spread; and
- thermal, software-power-cap, and hardware-power-brake events/counters.

Retain CPU, NVMe, starting temperature, sequence, and session/block identifiers
as nuisance covariates. Do not claim a fan-policy effect from a single run or
from pooled 250 ms samples.

## Sequential expansion

If the 350 W block passes, refit the power-by-fan allocation response using the
validated 200, 250, 300, and 350 W populations. Choose 400 W next unless
cross-validated error or curvature selects a safer asymmetric or intermediate
cell. Each new power level repeats qualification before measurement. Do not
infer 500–550 W low-fan safety from the lower-power surface.

The static spine is the baseline for the later persistent controller study.
Dynamic policies must be compared against these same admitted static cells,
including EQ50 and the best validated lower-biased allocation.

## Runner

[`run-static-fan-power-block.sh`](run-static-fan-power-block.sh) implements
read-only check/dry-run modes, frozen manifests, order validation, exclusive
block locking, qualification and measurement gates, fail-stop behavior, and
block checksums. It never loads the GPUs without explicit `--run`.
