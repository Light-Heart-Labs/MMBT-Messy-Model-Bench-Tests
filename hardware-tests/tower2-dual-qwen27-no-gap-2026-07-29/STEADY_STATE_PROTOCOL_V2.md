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
