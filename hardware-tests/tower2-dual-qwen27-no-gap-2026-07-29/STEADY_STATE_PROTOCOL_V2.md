# Fixed-fan steady-state protocol v2

## Why this revision exists

The first three 250/250 W, fixed-30/30% runs reproduced the same physical
operating point:

| Run | Mean top-bottom temperature | Mean top-bottom clock | Throughput bottom/top | v1 top slope |
|---|---:|---:|---:|---:|
| R1 | 16.479 C | -31.677 MHz | 0.9600 / 0.8533 req/s | +0.0582 C/min |
| R2 | 16.408 C | -31.077 MHz | 0.9600 / 0.8533 req/s | +0.4288 C/min |
| R3 | 16.423 C | -32.582 MHz | 0.9600 / 0.8533 req/s | +0.2186 C/min |

R1 passed the original absolute 0.1 C/min slope gate while R2 and R3 failed.
The GPU temperature channel reports integer degrees, so the timing of a single
one-degree transition inside a three-minute regression can dominate a
low-slope result. R2 and R3 remain excluded under the rule active when they
ran. This revision is prospective and creates new cell IDs; it does not
reclassify old evidence.

## V2 admission rule

`v2-fixed-quantized` is restricted to runs with:

- fixed fan targets on both GPUs;
- at least 900 measured seconds after the standard loaded warmup;
- the existing power, utilization, sample-completeness, isolation, event, fan
  telemetry, and fan-target-tracking gates;
- five complete one-minute temperature bins covering the final five minutes;
- a range of no more than 1.0 C across the five one-minute temperature
  medians; and
- an absolute linear slope of no more than 0.35 C/min across those five
  minute medians.

The legacy three-minute raw-sample slope is still reported for continuity but
does not determine v2 admission. The one-degree median range explicitly
matches the sensor quantum; the five-bin slope prevents a monotonic one-degree
creep from being treated as a flat plateau. Fixed-fan duty must separately
remain steady within the existing 0.2 percentage-point/minute rule.

## Cell naming and comparability

V2 results use new cell IDs ending in `-V2-15M`. They must not be pooled with
the earlier ten-minute v1 cell for formal validation. The first fixed-fan
matrix uses 15-minute measured windows, a five-minute preflight idle soak,
two-minute loaded warmup, and 1 Hz physical fan telemetry.

The initial crossed-fan comparison at 250/250 W and constant 100 percentage
points of commanded fan duty is:

1. `NG-FAN-EQ50-SYM250-V2-15M` - bottom/top 50/50%;
2. `NG-FAN-B70-T30-SYM250-V2-15M` - bottom/top 70/30%;
3. `NG-FAN-B30-T70-SYM250-V2-15M` - bottom/top 30/70%.

This directly tests whether extra bottom-card fan work benefits the top card,
whether direct top-card fan work is more effective, and whether a cooler lower
card can carry useful airflow duty for the stack at constant aggregate command.
Each cell requires at least three admissible independent replicates before its
means become validated model inputs.

## V3HOST whole-system reset amendment

The paired 200 W and 300 W crossover blocks demonstrated that GPU core
temperature alone is not a sufficient preflight reset variable. Later runs
were systematically warmer even after both GPUs passed the 45 C/0% utilization
gate and completed the five-minute soak. CPU and NVMe telemetry rose across
the same execution sequence, showing that heat remained in the chassis and
supporting components after the GPU cores appeared cool.

`V3HOST` is a prospective comparability amendment. It retains the complete
`v2-fixed-quantized` admission rule and adds configurable whole-system start
gates to the harness. The first Tower2 300 W cells require all of the following
before the five-minute continuous soak begins:

- GPU0 and GPU1 at or below 45 C and 0% utilization;
- CPU Tctl at or below 70 C;
- hottest NVMe Composite sensor at or below 41.9 C; and
- external GPU request sources quiesced throughout the gate and soak.

The preflight CSV records GPU temperatures/utilization, CPU Tctl, hottest NVMe
Composite, monotonic time, and gate state every five seconds. Any threshold
violation resets the continuous-soak clock. The preflight timeout is
configurable and is 3600 seconds for these cells.

These thresholds are internal Tower2 heat-state controls, not universal
hardware limits or calibrated ambient substitutes. They were selected to
approximate the early-session host state observed in the campaign. Results
using the stricter reset use new cell IDs containing `V3HOST`; they are not
silently pooled with earlier V2 replicates. Each V3HOST cell independently
requires at least three admissible replicates.

The first V3HOST exposure provided direct evidence that the additional reset
variables are material. Both GPU cores became eligible while the hottest NVMe
was still above threshold; the harness waited approximately 9 minutes 45
seconds before the five-minute continuous soak could begin. It then completed
304 seconds without a reset and began the run from 32/34 C GPUs, 58.1 C CPU
Tctl, and 41.9 C hottest NVMe. GPU-only preflight would have admitted this
session substantially earlier.

### Paired-block matching and covariates

Maximum start gates reduce hidden heat-state variation but do not make starts
identical: a later run may cool below a threshold before setup begins. For
paired fan-policy interpretation, each block therefore records and compares
the final eligible GPU0/GPU1 temperatures, CPU Tctl, and hottest NVMe
temperature. A prospective tightly matched block requires absolute between-run
start differences no larger than:

- 3 C for each GPU;
- 3 C for CPU Tctl; and
- 1 C for hottest NVMe Composite.

These tolerances are admission limits for a paired contrast, not evidence that
the remaining mismatch is negligible. Analyses retain all start values plus
loaded CPU and NVMe means as nuisance covariates, report both full-window and
last-five-minute responses, and alternate policy order across blocks. A run
outside the pair tolerances may remain an admissible replicate for its
individual V3HOST cell but cannot count as a tightly matched causal pair.

The first 300 W V3HOST block met the boundary tolerances, but its 40/60 run
started 3/2 C cooler on GPU0/GPU1 and 1 C cooler on NVMe than its 60/40 run.
Loaded CPU and NVMe means were also 1.930 and 1.251 C cooler. Its raw fan-policy
contrast is therefore published as preliminary and covariate-confounded.
