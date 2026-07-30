# Tower2 stacked-GPU comprehensive research and test plan

**Program:** Adjacent RTX PRO 6000 Blackwell workstation GPU thermal, power, airflow, and inference-performance characterization  
**Test platform:** Tower2  
**Primary measured configuration:** Two directly adjacent cards with no open-slot gap  
**Forecast targets:** Two-, three-, and four-card stacks across power, ambient, airflow, spacing, and workload conditions  
**Canonical workload:** Independent Qwen3.6-27B AWQ-INT4 vLLM engine per loaded GPU  
**Document status:** Execution-ready plan, version 1.0

## 1. Program objective

Produce a public, reproducible engineering dataset and predictive model that helps system builders answer:

- How do adjacent 600 W-class GPUs behave at different individual and total stack power levels?
- How much hotter is each physical stack position?
- How much boost frequency and application performance are lost as cards heat-soak?
- How much heat from one card affects its neighbor, and in which direction?
- What power allocation gives the best aggregate throughput without forcing the hottest card into thermal-limit operation?
- How do spacing, chassis airflow, ambient temperature, card order, and workload change the answer?
- What should be expected from three- and four-card stacks when only two-card measurements are currently available?
- Which forecasts are well supported, and which require physical validation?

The final product is not merely a pass/fail thermal report. It is a versioned dataset, an auditable experimental record, a thermal/performance model, and a set of design-reference tables with uncertainty bounds.

## 2. Current evidence and motivating observations

The current no-gap campaign has established four important anchors:

| Condition | GPU0 bottom | GPU1 top | Primary observation |
|---|---|---|---|
| 250/250 W, 10 min | 51.85°C, 30.7% fan, 803.6 MHz | 66.97°C, 40.1% fan, 775.5 MHz | 15.12°C positional delta; no thermal events |
| 500/500 W, 10 min | 70.20°C, 42.9% fan, 2509 MHz | 89.57°C, 78.5% fan, 2104 MHz | 19.37°C delta; top loses substantial boost; 1.054 s SW thermal event |
| 600/400 W, 30 min | 80.59°C, 49.8% fan, 2727 MHz | 87.94°C, 67.8% fan, 1344 MHz | Top remains hotter while consuming 200 W less |
| 600/600 W attempt | 74.97°C, 45.6% fan | 92.65°C, 99.4% fan | Aborted at 96°C; confirmed top-card thermal boundary |

These results show a repeatable positional asymmetry, nonlinear frequency consequences, and a no-gap upper boundary. They do **not** yet separate:

- physical position from individual card identity;
- self-heating from neighbor heating;
- intake restriction from hot-air recirculation;
- absolute temperature from rise above local inlet temperature;
- Qwen-specific behavior from general compute or memory behavior.

Those are the identification problems this plan resolves.

## 3. Research questions and hypotheses

### 3.1 Primary questions

1. What are the self-heating curves for the top and bottom physical positions?
2. What is the directional coupling coefficient from bottom to top and top to bottom?
3. At what power does the top card transition from mild boost loss to meaningful thermal derating?
4. How should a fixed total GPU power budget be distributed across positions?
5. How does the answer change with ambient temperature and airflow?
6. Does the observed asymmetry follow the physical position or the individual GPU?
7. Can a two-card thermal network predict safe operating envelopes for three and four cards?

### 3.2 Testable hypotheses

- **H1 — position effect:** At equal power and workload, the top position has higher local inlet and core temperatures than the bottom position.
- **H2 — directional coupling:** Bottom-card power has a larger effect on top-card temperature than top-card power has on the bottom card.
- **H3 — nonlinear knee:** Top-card fan demand and clock loss accelerate nonlinearly above a power-dependent thermal knee.
- **H4 — sub-threshold derating:** Heat-associated loss of boost begins before NVIDIA reports a software or hardware thermal-limit event.
- **H5 — allocation benefit:** A bottom-heavy power allocation produces more aggregate throughput than an equal allocation at the same total stack power.
- **H6 — identity confound:** Some portion of the gap follows the physical GPU because of cooler contact, fan performance, or voltage-frequency efficiency.
- **H7 — workload dependence:** Prefill-heavy, decode-heavy, compute-heavy, and memory-heavy workloads yield different temperature and frequency surfaces at the same stated power.
- **H8 — stack compounding:** A three- or four-card stack incurs more than a simple linear multiple of the two-card top-position penalty when airflow resistance and inlet heating compound.

## 4. Scope

### 4.1 In scope

- Two installed RTX PRO 6000 Blackwell Workstation Edition cards.
- No-gap, spaced, panel, duct, fan, and card-order configurations.
- 250–600 W per-GPU power limits.
- Single-card, symmetric dual-card, and asymmetric dual-card loading.
- Dense Qwen inference and selected synthetic/application workload classes.
- GPU, host, environmental, electrical, acoustic, and workload telemetry.
- Steady-state and transient thermal modeling.
- Bounded three- and four-card forecasts.

### 4.2 Out of scope for the first release

- Claiming a three- or four-card forecast is physically measured.
- Production reliability or lifetime qualification.
- Component-level heatsink or board modification.
- Warranty, RMA, or vendor certification conclusions.
- Generalizing results to different GPU coolers, chassis, or fan systems without qualification.

## 5. Definitions

- **Explicit thermal-limit event:** NVIDIA `SW Thermal Slowdown` or `HW Thermal Slowdown` reason/counter is active.
- **Power-limit derating:** Clock is reduced to remain inside the configured power limit.
- **Heat-associated boost loss:** A repeatable reduction in achievable clock or performance with increasing temperature at fixed power, whether or not an explicit thermal-limit flag is set.
- **Steady state:** Last-three-minute temperature slope is less than 0.1°C/min and fan slope is less than 0.2 percentage points/min.
- **Anchor cell:** A condition repeated across sessions/configurations to estimate measurement and day-to-day variation.
- **Measured / interpolated / extrapolated:** Direct observation / estimate inside the measured factor space / estimate outside the physically measured stack-size or factor space.

## 6. Instrumentation

### 6.1 Required before the main matrix

Install calibrated sensors with a common timestamp:

| Sensor | Location | Minimum specification | Purpose |
|---|---|---|---|
| Room ambient | 1–2 m ahead of chassis intake | ±0.5°C, 1 Hz | Session normalization |
| Chassis intake | Immediately before primary intake | ±0.5°C, 1 Hz | System inlet temperature |
| GPU0 local intake | At bottom-card fan inlet without obstructing flow | Thin probe, ±0.5°C | GPU0 thermal rise |
| GPU1 local intake/gap | At top-card fan inlet/inter-card channel | Thin probe, ±0.5°C | Direct coupling evidence |
| GPU0 exhaust | Downstream of bottom cooler | ±1°C | Removed heat |
| GPU1 exhaust | Downstream of top cooler | ±1°C | Removed heat |

Strongly preferred:

- relative humidity;
- chassis fan RPM and command;
- differential pressure across the stack or repeatable airflow measurement;
- wall power with timestamped logging;
- PSU exhaust temperature;
- sound level at a fixed one-meter position;
- photographs and dimensional measurements of the card gap, obstructions, panel, filters, and ducts.

Do not use an IR camera as the sole quantitative temperature source. Reflections, emissivity, and lack of line-of-sight to the active inlet limit comparability; use it as supporting visualization.

### 6.2 GPU telemetry

Archive at 1 Hz for all runs. Add a 100–250 ms channel for transient fields when supported:

- wall and monotonic timestamp;
- GPU UUID, serial, PCIe address, index, physical position;
- instantaneous and one-second-average power;
- requested, current, enforced, default, minimum, and maximum power limits;
- GPU, memory, hotspot, target, slowdown, and T.Limit values where exposed;
- graphics, SM, video, and memory clocks;
- GPU, memory, SM, tensor, DRAM, PCIe, and NVLink activity where applicable;
- P-state;
- fan percentage and RPM when available;
- framebuffer and BAR1 use;
- clock-event bitmask;
- cumulative software-power, software-thermal, hardware-thermal, and power-brake counters;
- ECC, XID, PCIe replay, link-state, and driver health events.

NVIDIA DCGM profiling should be evaluated for higher-frequency activity data. Record unsupported fields as null rather than silently omitting them.

### 6.3 Host and facility telemetry

- CPU package/Tctl, CCD, frequency, utilization, and package power;
- DIMM temperatures where available;
- NVMe and motherboard temperatures;
- chassis fan RPM;
- PSU and wall input power;
- AC input voltage if the meter supports it;
- room ambient and humidity;
- process/container inventory;
- kernel, driver, firmware, VBIOS, CUDA, DCGM, vLLM, model, quantization, and container-image versions.

### 6.4 Workload telemetry

- deterministic prompt-set ID and checksum;
- random seed;
- input/output token counts;
- context length;
- concurrency, batch, queue depth, and cache state;
- prefill and decode tokens/s;
- total tokens/s;
- time to first token;
- inter-token latency;
- request throughput;
- P50/P95/P99 request latency;
- errors, retries, cancellations, and incomplete requests;
- GPU-seconds, joules/request, tokens/joule, and tokens/s/W.

## 7. Experimental factors

| Factor | Planned levels |
|---|---|
| GPU0/bottom power | 0/idle, 250, 300, 350, 400, 450, 500, 550, 600 W |
| GPU1/top power | 0/idle, 250, 300, 350, 400, 450, 500, 550, 600 W |
| Spacing | No gap, one open slot, intended final spacing |
| Card order | Original, physically swapped |
| Panel | Closed, open |
| Airflow | Stock, directed intake/duct, deliberately reduced but safe |
| Fan policy | Automatic; selected fixed points if supported and safe |
| Ambient | Target bins at 15, 20, 25, 30, and 35°C; 40°C only as a controlled stress extrapolation/validation case |
| Workload | Dense Qwen, prefill-heavy, decode-heavy, compute-heavy, memory-heavy, burst/idle |
| Duration | Idle 10 min, bump 2 min, standard 10 min, validation 30 min, endurance 60–120 min |

## 8. Run protocol

### 8.1 Preflight

1. Confirm host identity, GPU UUID/serial-to-position mapping, and physical configuration.
2. Photograph and measure the configuration.
3. Confirm no heavy-run lock is held.
4. Confirm no queued/running production requests.
5. Confirm both GPUs have returned to the standardized idle baseline.
6. Record environmental sensors for at least five idle minutes.
7. Capture `nvidia-smi -q`, topology, driver, container, and service state.
8. Confirm power limits can be restored automatically.
9. Confirm telemetry sample clocks are synchronized.
10. Confirm emergency cleanup traps and stop files.

### 8.2 Standard cell

1. Start raw telemetry before changing services or power limits.
2. Isolate required GPU services.
3. Apply per-GPU power limits.
4. Start identical workload engines with verified GPU pinning.
5. Warm up for 120 seconds.
6. Require trailing-30-second mean power ≥95% of each requested cap and utilization ≥99%.
7. Measure for ten minutes.
8. Drain admitted requests.
9. Record a 60-second loaded-to-idle cooldown.
10. Capture after-state counters.
11. Restore default caps and services.
12. Confirm cleanup and zero queued requests.

### 8.3 Acceptance criteria

A single replicate is admissible when:

- sample completeness is at least 95%;
- both workload instances remain healthy;
- intended utilization and power gates are met;
- no uncontrolled production work overlaps;
- required environmental sensors are complete for any transferable claim;
- time synchronization error is documented and acceptable;
- no emergency abort occurs;
- final thermal slope satisfies the steady-state criterion.

A run labeled `not_steady`, environmentally unnormalized, contaminated, aborted, or otherwise outside these gates remains a useful diagnostic or safety pilot, but it does not count toward validation `n`.

A test cell or study conclusion is validated only when:

- at least three admissible, independent replicates (`n >= 3`) exist for every condition supporting the conclusion;
- replicates span at least three sessions or randomized blocks unless a documented design constraint prevents it;
- all replicate IDs, exclusions, and exclusion reasons are published;
- between-replicate dispersion and confidence or prediction intervals are reported;
- no invalid or qualified pilot is silently substituted for a missing valid replicate.

### 8.4 Safety and stop criteria

Keep the existing 96°C GPU emergency cutoff unless a lower, manufacturer-supported limit is selected. Stop immediately for:

- GPU temperature at the cutoff;
- any hardware thermal slowdown or hardware power-brake event;
- an XID, ECC, PCIe, driver, or container failure;
- unexpected power above the enforced limit;
- loss of telemetry;
- sustained 100% fan with temperature still rising toward the cutoff;
- host CPU, motherboard, storage, PSU, or facility readings outside their verified operating limits.

The existing no-gap 600/600 W condition is a known failed cell and must not be repeated unchanged. Any 550–600 W top-card condition requires a two-minute safety bump before a standard run.

## 9. Test matrix

### 9.1 Tier 0 — completed pilots and anchors

| ID | Bottom/top power | Duration | Status |
|---|---:|---:|---|
| NG-SYM-250-R1 | 250/250 W | 10 min | PASS pilot; not validated until n=3 |
| NG-SYM-500-R1 | 500/500 W | 10 min | PASS pilot; 1.054 s top SW thermal; not validated until n=3 |
| NG-ASYM-600-400-R1 | 600/400 W | 30 min | PASS pilot; not validated until n=3 |
| NG-SYM-600-R1 | 600/600 W | Intended 30 min | Safety abort near 5 min; failed pilot, never counted toward n |

### 9.2 Tier 1 — essential before changing spacing

#### A. Idle and self-heating controls

| ID family | Bottom/top load | Power levels | Repeats |
|---|---|---|---:|
| NG-IDLE | Idle/idle | Default | 3 sessions |
| NG-SINGLE-B | Loaded/idle | 250, 400, 500, 600 W | 3 valid replicates each |
| NG-SINGLE-T | Idle/loaded | 250, 400, 500, 600 W | 3 valid replicates each |

These eight loaded conditions identify self-heating and the passive obstruction effect of the adjacent idle card. Qualified pilots do not reduce the three-valid-replicate requirement.

#### B. Symmetric response curve

| ID | Bottom/top | Action |
|---|---:|---|
| NG-SYM-300-R1 | 300/300 W | Standard |
| NG-SYM-350-R1 | 350/350 W | Standard |
| NG-SYM-400-R1 | 400/400 W | Standard |
| NG-SYM-450-R1 | 450/450 W | Standard |
| NG-SYM-550-B1 | 550/550 W | Two-minute bump |
| NG-SYM-550-R1 | 550/550 W | Standard only if bump passes |

#### C. Directional coupling sweeps

Hold one card at 250 W while varying its neighbor:

| Sweep | Cells, bottom/top |
|---|---|
| Bottom-to-top coupling | 350/250, 450/250, 550/250, 600/250 W |
| Top-to-bottom coupling | 250/350, 250/450, 250/550, 250/600 W |

Top-card 550 and 600 W cells require bump tests.

#### D. Fixed-total-power allocation

| Total power | Allocation cells, bottom/top |
|---:|---|
| 800 W | 550/250, 450/350, 400/400, 350/450, 250/550 |
| 1000 W | 600/400, 550/450, 500/500, 450/550, 400/600 |

Every standard-response, coupling, and allocation condition requires at least three valid replicates before it supports a validated conclusion. Several endpoints overlap other phases; a valid run may satisfy multiple matrix families when its metadata declares those mappings.

#### E. Replication and card identity

- Complete at least three valid 250/250, 400/400, and 500/500 replicates across separate sessions.
- Physically swap the two cards.
- After the swap, repeat 250/250, 400/400, and 500/500.
- Preserve UUID/serial mapping rather than relying on GPU index.

### 9.3 Tier 2 — fan-controlled airflow identification

Automatic-fan runs are closed-loop operating points: temperature changes fan
speed, and fan speed changes temperature. They describe the stock system, but
cannot by themselves identify a position penalty or thermal resistance at
equal cooling effort. Fan duty and actual RPM must therefore be treated as
controlled inputs as well as measured outputs.

Tower2 exposes four physical GPU fans through `nvidia-settings`, including
commanded duty, current duty, and per-fan RPM. The verified mapping is fans
0–1 for GPU0/bottom and fans 2–3 for GPU1/top. Manual target assignments fail
under the current X-server configuration, so fixed-fan execution remains
gated on a controlled Coolbits configuration/restart and a fail-safe idle
validation; advertised attributes alone are not proof that control works.

Run two complementary families:

1. **Automatic-fan operational envelope:** retain the stock controller and
   measure the temperatures, fan response, clocks, throughput, and throttle
   state a real deployment would produce.
2. **Fixed-fan physics surface:** hold fan duty/RPM constant while varying
   power, so positional self-heating and directional cross-heating can be
   identified without controller feedback hiding or amplifying them.

At minimum, run three valid replicates of:

| Power condition, bottom/top | Equal fixed fan duties | Crossed fan duties |
|---|---|---|
| 250/250 | 30/30, 50/50, 70/70, 85/85 | 30/70, 70/30, 50/80, 80/50 |
| 400/400 | 50/50, 70/70, 85/85 | selected high-information pairs |
| 500/500 | 70/70, 85/85, 100/100 bump first | selected safe pairs |
| 250/idle and idle/250 | 30/30, 50/50, 70/70, 85/85 | sweep the idle neighbor's fan |

The single-loaded crossed-fan cells directly test the “fans in series” idea:
hold the loaded card's power and fan fixed, then change only the neighboring
card's fan. A change in loaded-card temperature, local inlet temperature, or
required fan RPM measures neighbor-assisted or neighbor-disrupted airflow.
Repeat in both directions because bottom-to-top and top-to-bottom coupling need
not be symmetric.

Do not normalize temperature by dividing by fan percentage. Fan percentage is
not airflow, RPM is not necessarily linear with duty, and heat transfer is
nonlinear with flow. Fit fan duty and RPM as nonlinear predictors, including
cross-card interaction terms. Continue recording per-GPU fan duty in every
primary NVIDIA sample and record all four individual physical fan RPMs at
least once per second.

Every manual-fan run requires a tested automatic-control restoration path on
normal exit and every trap, an independent emergency temperature cutoff, a
short bump test before a new high-power/low-fan combination, confirmation that
commanded duty and actual RPM agree, and exclusion if a fan stalls or control
is lost.

### 9.4 Tier 2 — configuration anchors

For each configuration below, measure three valid replicates of 250/250, 400/400, and 500/500:

- side panel open;
- directed intake fan or duct;
- one open-slot gap;
- intended final spacing;
- fixed fan points if supported;
- deliberately reduced but safe chassis airflow.

If time is constrained before spacing changes, prioritize no-gap card swap, side-panel open, and directed-intake anchors.

### 9.5 Tier 3 — workload generalization

At 250/250, 400/400, and 500/500, run at least three valid replicates of:

- current dense Qwen request mix;
- long-context prefill-heavy workload;
- decode-heavy workload;
- compute-heavy matrix workload;
- memory-bandwidth-heavy workload;
- burst/idle service trace.

### 9.6 Adaptive matrix expansion

Do not automatically execute the complete 8×8 dual-power grid. After Tier 1:

1. fit the initial response surface;
2. predict every 50 W grid cell;
3. calculate uncertainty and curvature;
4. choose the next cells by maximum expected information gain;
5. preferentially sample thermal knees, high-uncertainty regions, and allocation optima;
6. stop adding cells when cross-validated error and forecast intervals meet the publication targets.

## 10. Statistical design

### 10.1 Blocking and order

- Treat each physical configuration and ambient bin as a block.
- Randomize safe power-cell order inside a block.
- Interleave anchor replicates to estimate drift.
- Do not run all low-power points followed by all high-power points.
- Record cold-start and hot-start state explicitly.

### 10.2 Replication

- At least three valid repeats for every test cell or study used for validation.
- Safety bumps and exploratory boundary probes may remain pilots at lower n, but cannot support a validated operating limit until three admissible confirmations exist.
- Repeat any cell whose key metric differs from the fitted surface by more than three times the anchor repeat standard deviation.
- Excluded, aborted, contaminated, and non-steady runs are published with reasons but do not count toward n.

### 10.3 Primary response variables

- steady GPU and local-inlet temperature;
- temperature rise above local inlet;
- fan duty;
- graphics/SM clock;
- tokens/s and latency;
- tokens/s/W and tokens/joule;
- explicit thermal-event duty;
- time to 63.2% and 90% of steady-state temperature rise.

### 10.4 Quality statistics

Publish mean, median, standard deviation, P05/P95, maximum, first/last-window values, slope, sample count, and missing-sample fraction. For model validation publish:

- mean absolute error;
- root mean square error;
- maximum absolute error;
- prediction-interval coverage;
- leave-one-cell-out error;
- held-out configuration error;
- replicate coefficient of variation.

## 11. Derived engineering quantities

For each card/run calculate:

```text
temperature_rise = T_gpu - T_local_inlet
apparent_thermal_resistance = temperature_rise / board_power
clock_derating = clock_cool_reference - clock_observed
thermal_event_fraction = thermal_counter_delta / measured_duration
energy = integral(board_power dt)
performance_per_watt = tokens_per_second / board_power
energy_efficiency = output_tokens / joules
```

Directional coupling:

```text
bottom_to_top_coupling(P_bottom, P_top)
  = T_top(both loaded) - T_top(top-only at same P_top)

top_to_bottom_coupling(P_top, P_bottom)
  = T_bottom(both loaded) - T_bottom(bottom-only at same P_bottom)
```

Also publish:

- top-minus-bottom temperature, fan, clock, throughput, and efficiency deltas;
- MHz/°C at fixed power;
- percentage-points-of-fan/°C;
- temperature/neighbor-watt;
- total stack throughput per total stack watt;
- hottest-card margin to cutoff and operating limit;
- optimal allocation under temperature, noise, and performance constraints.

## 12. Predictive model

### 12.1 Primary physics-informed model

Use a coupled lumped thermal-resistance/capacitance network:

```text
C_i dT_i/dt =
    P_heat_i
  - (T_i - T_local_inlet_i) / R_self_i
  - sum((T_i - T_j) / R_coupling_ij)

T_local_inlet_i =
    T_ambient
  + directional_heat_from_neighbors
  + stack_airflow_penalty(position_i, stack_size, configuration)
```

Fit self-heating from single-card controls. Fit directional coupling from asymmetric dual-card controls. Fit transient capacitance/time constants from warmup and cooldown. Fit automatic fan response and fixed-fan thermal response separately:

```text
fan_i = f(T_i, P_i, configuration, card_identity)
theta_bottom =
    R_bb(F_bottom, F_top) * P_bottom
  + R_bt(F_bottom, F_top) * P_top

theta_top =
    R_tt(F_top, F_bottom) * P_top
  + R_tb(F_top, F_bottom) * P_bottom

clock_i = g(P_i, T_i, F_i, workload, card_identity)
performance_i = h(clock_i, SM_activity_i, DRAM_activity_i, workload)
```

Here `theta_i` is temperature rise above the card's measured local inlet, not
raw GPU temperature. The cross-fan arguments are intentional: a neighboring
fan may assist, starve, or turbulently disturb the loaded card. These fitted
resistances are nonlinear surfaces, not constants.

### 12.2 Empirical cross-check

Fit a hierarchical nonlinear response surface or generalized additive model:

```text
response ~ f(P_self) + f(P_neighbor) + P_self:P_neighbor
         + f(fan_self_RPM) + f(fan_neighbor_RPM)
         + fan_self_RPM:fan_neighbor_RPM
         + position + card_identity + ambient + airflow
         + workload + configuration + random_session_effect
```

Use the empirical model for interpolation and residual checking. Do not rely on a black-box model alone for three- or four-card extrapolation.

### 12.3 Three- and four-card extrapolation

Construct virtual positions from bottom to top. Include:

- adjacent directional coupling;
- next-nearest-neighbor coupling with a fitted/assumed decay;
- cumulative inlet heating from upstream cards;
- position-dependent airflow resistance;
- stack-size airflow penalty.

Because two cards cannot identify stack-size airflow compounding, publish three forecast bands:

- **Lower bound:** measured self-heating plus nearest-neighbor coupling; no added stack airflow penalty.
- **Base case:** cumulative directional coupling and the best-supported airflow penalty.
- **Upper bound:** conservative compounding calibrated to the hottest measured no-gap behavior and reduced-airflow anchors.

The upper/base/lower spread is part of the result, not an inconvenience to hide.

### 12.4 Forecast scenario grid

Generate forecasts for:

- stack size: 2, 3, and 4;
- equal caps: 250–600 W in 50 W increments;
- bottom-heavy, top-heavy, and center-heavy allocation patterns;
- fixed total stack power;
- ambient: 15, 20, 25, 30, and 35°C;
- stock, improved, and degraded airflow;
- automatic and selected fixed fan policies;
- dense steady load and bursty service load;
- failed/obstructed fan as a clearly labeled fault scenario.

For each virtual card publish:

- local inlet and GPU temperature;
- fan duty;
- clock;
- throughput and latency;
- efficiency;
- probability of explicit thermal-limit operation;
- time to equilibrium;
- margin to cutoff;
- 50%, 80%, and 95% prediction intervals.

## 13. Model validation and decision gates

### Gate 1 — instrumentation

Do not fit transferable thermal resistance or ambient forecasts until local inlet temperatures are logged.

### Gate 2 — identifiability

Do not fit a stack-coupling model until both single-card directions and both asymmetric sweep directions exist.

### Gate 3 — repeatability

Primary anchors should have:

- temperature coefficient of variation below 2%;
- steady clock coefficient of variation below 3%;
- power coefficient of variation below 1%;
- no unexplained configuration drift.

If not, investigate environment, workload, or instrumentation before expanding the matrix.

### Gate 4 — interpolation accuracy

Target held-out two-card errors:

- temperature MAE ≤2°C;
- fan MAE ≤5 percentage points;
- clock MAE ≤5%;
- throughput MAE ≤5%.

### Gate 5 — extrapolation status

Three- and four-card predictions remain `extrapolated` until checked by:

- at least one physical three- or four-card configuration, or
- a validated CFD/airflow model with measured boundary conditions.

## 14. Data architecture

### 14.1 Directory layout

```text
stacked-gpu-study/
  README.md
  methodology/
    COMPREHENSIVE_RESEARCH_AND_TEST_PLAN.md
    DATA_DICTIONARY.md
    MODEL_CARD.md
  hardware/
    inventory.json
    layout/
    sensor-calibration/
  runs/
    <run-id>/
      run-config.json
      environment.csv
      gpu-telemetry.csv
      dcgm-telemetry.csv
      host-telemetry.csv
      workload.csv
      events.log
      nvidia-before.txt
      nvidia-after.txt
      summary.json
      REPORT.md
  normalized/
    run_manifest.csv
    gpu_samples.parquet
    run_summary.csv
    coupling_coefficients.csv
  models/
    thermal-network-v1.json
    response-surface-v1.json
    validation-v1.json
  forecasts/
    forecast_2x.csv
    forecast_3x.csv
    forecast_4x.csv
  figures/
```

### 14.2 Run identifier

Use:

```text
<date>-T2-<spacing>-<workload>-B<bottomW>-T<topW>-<configuration>-R<replicate>
```

Example:

```text
2026-07-29-T2-NG-QWEN-B250-T250-STOCK-R1
```

### 14.3 Run manifest minimum columns

- run ID, timestamps, status, abort reason;
- GPU serial/UUID-to-position mapping;
- power limits;
- spacing, panel, duct, fan, filter, orientation;
- room/chassis/local inlet temperatures and humidity;
- workload and version identifiers;
- duration, warmup, cooldown, concurrency;
- telemetry versions and sample rates;
- report, raw-data, and figure paths;
- measured/interpolated/extrapolated status;
- operator notes and photo identifiers.

### 14.4 Preservation rules

- Raw files are immutable after capture.
- Corrections occur in versioned normalized data.
- Every aggregate must trace to run ID and raw sample range.
- Every chart includes source run IDs and sampling rate.
- Store checksums for raw artifacts.
- Use UTC timestamps plus monotonic elapsed time.
- Publish schema and units.

## 15. Publication package

The public release should include:

- concise executive summary;
- chassis and airflow diagram;
- high-resolution configuration photographs;
- complete methodology and test matrix;
- raw CSV and normalized Parquet data;
- machine-readable summaries;
- source scripts and environment lockfiles;
- temperature, frequency, fan, power, performance, and efficiency plots;
- directional-coupling tables;
- safe-operating-envelope plots;
- recommended power-allocation tables;
- 2× measured and 3×/4× forecast tables;
- model parameters, validation errors, uncertainty, and known limitations;
- data license and software license;
- release version and changelog.

Recommended table columns for builders:

| Stack | Position | Power cap | Ambient | Airflow/config | GPU temp | Fan | Clock | Tokens/s | Tokens/s/W | Thermal risk | Evidence |
|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|

Use `measured`, `interpolated`, or `extrapolated` in every row.

## 16. Execution sequence

### Session 1 — instrumentation and controls

1. Install/calibrate environmental sensors.
2. Capture three idle baselines.
3. Run bottom-only 250/400/500/600 W.
4. Run top-only 250/400/500 W and bump-test 600 W.

### Session 2 — symmetric curve

1. Repeat 250/250 anchor.
2. Run 300/300, 350/350, 400/400, and 450/450.
3. Repeat 400/400.
4. Bump-test 550/550; proceed only if safe.
5. Repeat 500/500 anchor.

### Session 3 — directional coupling

1. Bottom variable with top fixed at 250 W.
2. Top variable with bottom fixed at 250 W.
3. Add non-duplicate 800 W and 1000 W allocation cells.

### Session 4 — fan-controlled identification

1. Verify fan-to-GPU mapping and automatic-control fail-safe restoration.
2. Run fixed equal-fan 250/250 points at 30%, 50%, 70%, and 85%.
3. Run crossed-fan 250/250 points.
4. Run bottom-only and top-only neighbor-fan sweeps.
5. Expand fixed-fan tests to 400/400 and safe 500/500 points.

### Session 5 — identity and configuration airflow

1. Side-panel and directed-intake anchors.
2. Physically swap cards.
3. Repeat 250/250, 400/400, and 500/500.

### Session 6 — validation

1. Fit preliminary models.
2. Select adaptive high-information cells.
3. Run 30-minute validations at the thermal knee, recommended operating point, and safest high-throughput allocation.
4. Run one 60–120-minute endurance validation.

### After spacing is restored

Repeat 250/250, 400/400, and 500/500 at one-gap and intended-final spacing. These anchors convert the no-gap campaign into directly usable spacing guidance.

## 17. Resource estimate

A cold-start standard cell currently requires roughly:

- 2 minutes warmup;
- 10 minutes measured;
- 1 minute cooldown;
- approximately 3–5 minutes of engine startup, cleanup, and verification;
- additional time to return to a standardized idle temperature.

Budget 20–30 minutes per standard cell. The essential pre-spacing program is approximately 25–35 additional cells depending on overlap, safety failures, and adaptive stopping: about 10–18 test-hours across multiple sessions, plus sensor setup, card swap, analysis, and publication work.

## 18. Immediate next actions

1. Extend the harness to log all four GPU fan duties and actual RPM values.
2. Verify fan-to-GPU mapping and add fail-safe fixed-fan controls.
3. Acquire/install local inlet, inter-card, exhaust, and room temperature sensors.
4. Extend the harness to log those sensors and higher-frequency NVIDIA/DCGM fields.
5. Complete the fixed-fan 250 W identification matrix before interpreting a
   raw temperature delta as a position-only penalty.
5. Run the 250 W bottom-only and top-only controls.
6. Run 300/300 and 400/400 symmetric cells.
7. Fit the first self-heating and coupling curves before choosing the rest of the matrix.

## 19. References

- [NVIDIA `nvidia-smi` documentation](https://docs.nvidia.com/deploy/nvidia-smi/index.html) — power readings, temperature limits, clocks, event reasons, and cumulative counters.
- [NVIDIA DCGM profiling documentation](https://docs.nvidia.com/datacenter/dcgm/latest/learn/modules/profiling.html) — low-overhead GPU activity metrics and sampling.
- [NVIDIA DCGM exporter metrics](https://docs.nvidia.com/datacenter/dcgm/latest/reference/dcgm-exporter-metrics.html) — clocks, PCIe, health, and clock-event metric families.
- [Open Compute Project North Dome server design specification](https://www.opencompute.org/documents/north-dome-1s-server-design-specification-1v01-pdf) — example server thermal validation across 15–35°C inlet conditions.
