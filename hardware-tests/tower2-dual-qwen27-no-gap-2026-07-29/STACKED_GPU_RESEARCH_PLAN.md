# Stacked RTX PRO 6000 thermal and performance research plan

> The execution-ready program, detailed matrix, statistical design, data architecture, model-validation gates, and publication plan are in [`COMPREHENSIVE_RESEARCH_AND_TEST_PLAN.md`](COMPREHENSIVE_RESEARCH_AND_TEST_PLAN.md). This document remains the concise technical outline.

## Objective

Build a public, reproducible dataset and reduced-order model that:

1. describes measured two-card behavior across power, airflow, spacing, card identity, ambient temperature, and workload;
2. separates self-heating from directional neighbor heating;
3. forecasts temperature, fan duty, clock, throughput, efficiency, and thermal-limit risk for three- and four-card stacks;
4. reports forecast uncertainty and identifies conditions that require physical validation.

The model must distinguish NVIDIA's explicit thermal-limit events from heat-associated loss of boost below that threshold.

## Why equal-power burns are not sufficient

An equal-power dual-card run measures several effects at once:

- each card's own heat;
- heat transferred from its neighbor;
- intake restriction and recirculation caused by the adjacent card;
- position in the chassis airflow field;
- card-to-card cooler and silicon variation;
- fan-controller response;
- workload-specific power efficiency.

Forecasting a larger stack requires controlled runs that independently identify these terms.

## Reduced-order stack model

For card position `i`, model steady state as:

```text
T_gpu[i] = T_inlet[i] + self_rise(P[i], workload, fan[i])
T_inlet[i] = T_ambient + sum(coupling[j -> i] * heat[j]) + airflow_interactions
clock[i] = f(P[i], T_gpu[i], workload, card_identity)
performance[i] = g(clock[i], memory_activity[i], workload)
```

The first model should include:

- nonlinear self-heating versus power;
- directional nearest-neighbor coupling;
- cumulative inlet-air heating through the stack;
- an interaction term for airflow restriction as more adjacent cards are added;
- card-identity and physical-position effects;
- transient thermal time constants;
- uncertainty bands that widen for three- and four-card extrapolations.

Two-card data can identify the first-order terms and produce bounded forecasts. It cannot prove that airflow remains linear in a four-card stack. Any public forecast must state this limitation and should eventually be checked against at least one physical three- or four-card measurement or CFD model.

## Instrumentation required before expanding the matrix

### GPU telemetry

Record at 1 Hz for the full run and at 100–250 ms for transient/event capture when supported:

- monotonic and wall-clock timestamps;
- GPU index, UUID, serial number, PCIe address, and physical position;
- current, requested, default, and enforced power limits;
- instantaneous and one-second-average board power;
- cumulative energy where available;
- GPU, memory, hotspot, target, slowdown, and T.Limit temperatures where supported;
- graphics, SM, and memory clocks;
- P-state;
- GPU, SM, tensor, memory, PCIe, and encode/decode activity as applicable;
- fan percentage and fan RPM where available;
- clock-event bitmask and cumulative counters for software power cap, software thermal slowdown, hardware thermal slowdown, and hardware power brake;
- ECC, XID, PCIe replay, link-width, and link-generation changes;
- framebuffer and BAR1 usage.

NVIDIA DCGM profiling can sample supported activity metrics down to 100 ms. Preserve the exact driver, firmware, VBIOS, CUDA, DCGM, model, and container versions with every run.

### Environmental telemetry

This is essential for forecasts transferable to other server builds:

- room ambient temperature and relative humidity;
- bottom-card intake-air temperature;
- top-card intake-air temperature;
- temperature in the inter-card gap;
- exhaust temperature behind each card;
- chassis intake and exhaust temperatures;
- chassis fan RPM and commanded duty;
- approximate airflow or differential pressure across the GPU stack;
- side-panel state, filters, ducts, blanking plates, and chassis orientation;
- wall power and, if practical, PSU exhaust temperature;
- acoustic level at a fixed distance.

Report all GPU temperatures as both absolute temperature and rise above local intake temperature.

### Workload telemetry

- exact prompt corpus and deterministic seed;
- input and output token counts;
- concurrency, batch size, context length, and cache state;
- prefill tokens/s, decode tokens/s, total tokens/s;
- time to first token and inter-token latency;
- request throughput and P50/P95/P99 latency;
- errors, retries, and completed/aborted requests;
- tokens/joule and tokens/s per watt.

## Experimental controls

- Begin every comparable run with zero queued requests and a standardized idle temperature.
- Hold room/chassis fan configuration constant within a block.
- Randomize power-setting order where practical to reduce ambient drift bias.
- Repeat the center/reference cells at the beginning, middle, and end of a session.
- Use at least three replicates for anchor cells and any result used to fit a published model.
- Preserve raw samples; never publish only screenshots or aggregates.
- Record a photograph and physical diagram of every card/spacing/duct configuration.
- Swap the two physical cards before removing the no-gap layout. This separates card identity from physical position.

## Run protocol

1. **Idle baseline:** 10 minutes after both GPUs and queues reach idle.
2. **Safety bump:** 2 minutes at a new high-risk condition.
3. **Standard cell:** 120-second warmup, 10-minute measured window, 60-second cooldown.
4. **Steady-state gate:** accept a cell only if the last three minutes have a temperature slope below 0.1°C/min or report it as not yet at steady state.
5. **Validation cell:** 30 minutes at model knees, operational recommendations, and thermal boundaries.
6. **Endurance cell:** 60–120 minutes for the proposed production envelope and worst safe configuration.
7. **Cleanup:** restore services and defaults, then record the post-run idle state.

## Efficient no-gap matrix

Use an adaptive response-surface campaign rather than immediately executing all 64 combinations of an eight-by-eight grid.

### Phase A — symmetric power curve

| GPU0 bottom | GPU1 top | Purpose |
|---:|---:|---|
| 250 W | 250 W | Completed low-power anchor |
| 300 W | 300 W | Low/mid interpolation |
| 350 W | 350 W | Low/mid interpolation |
| 400 W | 400 W | Midpoint |
| 450 W | 450 W | Knee search |
| 500 W | 500 W | Completed high-temperature anchor |
| 550 W | 550 W | High-risk boundary screening |
| 600 W | 600 W | Existing safety-aborted boundary; do not repeat unchanged |

### Phase B — single-card self-heating controls

Run the loaded card at 250, 400, 500, and 600 W while its neighbor is present but idle:

- bottom loaded / top idle;
- top loaded / bottom idle.

These eight cells estimate each position's self-heating and reveal whether the idle adjacent card acts mainly as an obstruction, heat sink, or recirculation surface.

### Phase C — directional coupling sweeps

Hold one card at 250 W and sweep the other through 250, 350, 450, 550, and 600 W:

- bottom variable / top fixed at 250 W;
- top variable / bottom fixed at 250 W.

Then add fixed-total-power allocation lines:

| Total GPU power | Bottom/top allocations |
|---:|---|
| 800 W | 550/250, 450/350, 400/400, 350/450, 250/550 |
| 1000 W | 600/400 (completed), 550/450, 500/500 (completed), 450/550, 400/600 |

The direction-reversed cells are particularly valuable. Screen combinations with a 550–600 W top card using the two-minute safety protocol before committing to ten minutes.

### Phase D — adaptive fill

Fit the preliminary response surface, calculate prediction uncertainty across the full 250–600 W two-card grid, and run the cells with:

- the highest forecast uncertainty;
- the greatest curvature;
- a predicted thermal boundary;
- the strongest disagreement between repeated cells.

This extracts more information per test hour than blindly filling every 50 W combination. Publish both measured cells and interpolated cells with an explicit status column.

## Airflow and configuration blocks

At minimum, repeat anchor cells at 250/250, 400/400, and 500/500 for:

- current no-gap layout;
- one open-slot gap;
- intended final spacing;
- side panel open versus closed;
- stock chassis airflow versus an added directed intake fan or duct;
- auto fan control versus selected fixed fan duties if safely supported;
- original card order versus physically swapped cards.

For each block, do not change more than one physical factor at a time.

## Workload blocks

Use the same physical anchor cells with:

1. current dense Qwen inference;
2. prefill-heavy long-context inference;
3. decode-heavy inference;
4. compute-heavy matrix workload;
5. memory-bandwidth-heavy workload;
6. burst/idle cycling representative of shared inference service.

This prevents a Qwen-specific thermal response from being misrepresented as a universal GPU-stack result.

## Stack-aware fan-controller validation

After the static fan/power matrix is sufficiently populated, build a reliable
background service whose lower-card fans can respond to the temperature and
thermal trend of cards above them. The controller must preserve per-card local
safety overrides, restore NVIDIA automatic control on any failure, and log
every sensor input, decision, command, and physical-RPM response.

At selected symmetric and asymmetric anchor powers, compare stock automatic
control, equal static control, lower-biased static control, and dynamic
top/hottest-card-led control with at least three order-balanced replicates per
policy. Quantify temperature and clock spread, slowest-card latency, aggregate
throughput, fan RPM integral, remaining fan authority, controller stability,
and safety events.

Treat the four-card stack as the primary control-design target. Candidate
virtual-stack policies should model each lower fan bank as assisting all cards
above it, with distance-dependent weights and local safety taking precedence:

`fan_i = max(local_curve(T_i),
             assist_curve(weighted_max(T_i+1 ... T_top)))`.

Two-card results may define bounded candidate policies for three- and
four-card stacks, but controller benefit and stability must remain labeled
`forecast` until physically validated on an N-card stack or instrumented
surrogate.

## Derived quantities

Calculate per run and per GPU:

- temperature rise above local inlet, in °C;
- apparent thermal resistance, `(T_gpu - T_inlet) / power`, in °C/W;
- top-minus-bottom deltas for temperature, clock, fan, and throughput;
- directional coupling coefficient from neighbor power to local inlet/GPU temperature;
- clock derating slope at fixed power, in MHz/°C;
- fan-demand slope, in percentage points/°C and percentage points/W;
- thermal time constant and time to 90% of steady state;
- power-cap, thermal-limit, and power-brake duty fractions;
- tokens/s/W, tokens/joule, and performance loss per added °C;
- temperature and performance response to total stack power;
- safe power envelope versus ambient temperature.

## Three- and four-card forecast products

Forecast at least:

- equal caps from 250 through 600 W;
- fixed-total-power allocations;
- bottom-heavy, middle-heavy, and top-heavy power gradients;
- 20, 25, 30, 35, and 40°C inlet conditions;
- stock, improved, and degraded airflow;
- one failed or obstructed fan scenario;
- steady dense load and bursty inference.

For every virtual card position, publish:

- mean, P95, and upper confidence temperature;
- expected fan duty;
- expected graphics clock and performance;
- power-limit and thermal-limit probabilities;
- time to thermal equilibrium;
- safety margin to configured cutoff and NVIDIA operating limits.

Forecast tables must include `measured`, `interpolated`, or `extrapolated` status and a confidence interval. A four-card result should never be presented as a measured fact until physically validated.

## Public data package

Publish:

- `run_manifest.csv`: one row per run with hardware, configuration, environment, and workload metadata;
- `gpu_samples.parquet` and per-run CSV files: normalized time-series telemetry;
- `run_summary.csv`: one row per GPU per run;
- `coupling_coefficients.csv`: fitted directional/self-heating parameters;
- `forecast_3x_4x.csv`: scenarios, predictions, confidence bands, and measured/interpolated/extrapolated labels;
- `model.json` or an equivalent versioned parameter file;
- `MODEL_CARD.md`: assumptions, validation error, unsafe extrapolation regions, and version history;
- publication-quality temperature, frequency, fan, power, efficiency, and safe-envelope plots;
- a physical layout diagram and reproducible harness.

## Immediate priorities before changing the no-gap layout

1. Add local intake/inter-card/exhaust temperature sensing.
2. Complete single-card controls at 250, 400, 500, and 600 W.
3. Complete symmetric 300, 350, 400, and 450 W cells.
4. Screen 550/550 W rather than repeating unsafe 600/600 W.
5. Complete the two directional 250 W coupling sweeps.
6. Repeat 400/400 and 500/500 anchor cells for replication error.
7. Physically swap the two cards and repeat 250/250, 400/400, and 500/500.
8. Run 30-minute validations at the fitted thermal knee and recommended operating envelope.
9. Build and test the reliable stack-aware background fan service against
   stock auto and static policies before changing the no-gap layout.
10. Carry the validated control law, failure modes, and uncertainty into the
    three- and four-card forecast package.
