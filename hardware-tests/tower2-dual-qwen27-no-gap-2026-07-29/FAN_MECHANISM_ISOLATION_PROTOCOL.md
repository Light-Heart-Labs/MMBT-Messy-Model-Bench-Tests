# Own-fan versus neighbor-fan mechanism isolation

**Status:** prospective; execution-ready after an idle V3HOST preflight

**Configuration:** current no-gap layout

**First power anchor:** one loaded GPU at a continuously enforced 300 W cap

**Purpose:** separate local fan/power-budget effects from shared airflow

## 1. Identification problem

The matched dual-load experiments repeatedly associate more local RPM with a
small local clock/latency penalty, while the other card often gains clock.
They do not identify whether this comes from:

- fan electrical consumption inside the loaded card's board-power budget;
- local cooling/boost behavior;
- the neighbor's contribution to shared pressure and airflow;
- execution order or host heat state.

This protocol changes one fan source at a time.

## 2. Three-step blocked experiments

Each experiment is a paired three-step block with fan steps `30, 50, 70%`.
Use the three Latin-square orders below for the first three admissible blocks:

1. `30 -> 50 -> 70`
2. `50 -> 70 -> 30`
3. `70 -> 30 -> 50`

Each step receives a two-minute settling interval and a five-minute measured
interval. A block is therefore 21 measured/settling minutes after startup.
Run three independently initialized blocks per loaded position. Preserve
step-level telemetry and block identity; do not treat one-second samples as
independent replicates.

### Family A — own-fan saturated sweep

- loaded card: Qwen workload pinned at 300 W;
- loaded-card fan: stepped 30/50/70%;
- idle neighbor: 0% utilization, fan fixed at 50%;
- repeat with bottom loaded and top loaded.

Primary contrast: loaded-card clock, throughput, and silicon power availability
versus its own RPM while the software power cap is continuously active.

### Family B — neighbor-airflow sweep

- loaded card: same 300 W workload, own fan fixed at 50%;
- idle neighbor: 0% utilization, fan stepped 30/50/70%;
- repeat with bottom loaded and top loaded.

Primary contrast: loaded-card inlet/core temperature, clock, and throughput
versus neighbor RPM. The neighbor's fans cannot consume the loaded card's
board-power allowance, so a repeatable effect identifies shared airflow or
pressure coupling.

### Family C — power-headroom control

- set a 350 W cap on the loaded card;
- calibrate and freeze a workload that draws `270-300 W` without continuously
  asserting the software power-cap state;
- step the loaded-card fan 30/50/70%;
- keep the idle neighbor at 50%;
- repeat in both loaded positions.

If the own-RPM clock association disappears with headroom, fan/silicon budget
competition is supported. Persistence requires another mechanism.

Calibration determines workload concurrency only; calibration samples are not
inferential data and remain published as pilots.

## 3. Qualification and safety

Before the first 30% step for each loaded position and power condition:

- perform an isolated two-minute bump;
- require the V3HOST preflight and exact process isolation;
- confirm every physical fan maps to its commanded GPU;
- confirm emergency automatic-fan restoration on normal exit, signal, error,
  timeout, and temperature abort;
- use the existing 85 C campaign abort or a lower frozen threshold;
- require at least 8 C projected steady-state margin at the end of the bump;
- require no thermal/brake/ECC/Xid events and complete independent telemetry.

Abort the entire block rather than skipping to a cooler step when a step fails.
Retain the incomplete raw record.

## 4. Required channels

At 250 ms or faster where available:

- board power and enforced power limit;
- SW power-cap state and all thermal/brake counters;
- graphics clock distribution and independent NVML clock;
- GPU utilization, memory utilization, temperature;
- commanded duty and all physical fan RPMs for both cards;
- request/tokens throughput and latency;
- local inlet/inter-card temperature when instrumented;
- CPU, NVMe, chassis-fan, and execution-order covariates.

An external per-connector or wall-power meter is strongly preferred. NVIDIA
board power alone may not resolve a small fan-electrical component.

## 5. Prospective contrasts

Within each block, compare 70% versus 30% and estimate the slope across all
three steps. Fit:

`response ~ own_RPM + neighbor_RPM + temperature + cap_active
            + loaded_position + step_order + block`.

Report per position and pooled-with-interactions results. A mechanism is
promoted only when:

- its direction reproduces in all three admissible blocks;
- the paired confidence interval excludes a practically negligible band
  frozen before fitting;
- the result survives step-order and temperature adjustment;
- independent clock and workload-performance channels agree;
- no result is driven by a thermal-limit or request-boundary transient.

Family D, crossed dual-load confirmation, is run only after Families A-C
produce coefficients. It tests whether those coefficients prospectively
predict the existing 40/60 versus 60/40 redistribution at 300/300 W.
