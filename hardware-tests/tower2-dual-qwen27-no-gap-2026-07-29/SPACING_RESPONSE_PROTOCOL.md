# Tower2 spacing-response protocol

**Status:** prospective; freeze before the first post-no-gap run

**Purpose:** convert the no-gap campaign into a measured clearance-response
surface and bounded 2x/3x/4x engineering forecasts

**Primary comparison:** current 0 mm layout versus the prior approximately
3-inch layout, recorded as its measured shroud-to-shroud clearance

## 1. Design principle

The spacing campaign is an `A-B-A` experiment:

1. **A1 — no-gap:** finish and freeze the present campaign and its model.
2. **B — spacing response:** install the widely spaced reference, then sample
   mechanically available intermediate clearances.
3. **A2 — no-gap return:** repeat selected anchors after the spacing work.

The A2 return is mandatory. It estimates reseating, session, room, paste,
card-aging, and host-state drift that could otherwise be misattributed to gap.

The approximately 3-inch configuration is an endpoint, not evidence that the
response between 0 and 3 inches is linear. Restriction and recirculation are
expected to change most rapidly near contact.

## 2. Mechanical configuration record

Before powering a changed layout, record:

- `layout_id` and timestamp;
- exact minimum shroud-to-shroud clearance in millimeters at the front,
  middle, and rear, plus their minimum and mean;
- PCIe slot identities, card coordinates, card serial/UUID mapping, and which
  card is top/bottom;
- distance from each card to the side panel, chassis floor, PSU, cable bundle,
  and nearest intake obstruction;
- side-panel, chassis-fan, duct, filter, and cable state;
- front/side photographs with a ruler or scale in frame;
- whether a riser or support changes card attitude or blocks an inlet.

Model the measured minimum clearance. Preserve nominal targets such as
`0, 10, 20, 40, 76.2 mm` only as design labels. A PCIe-slot change is also a
categorical layout factor because it can change the surrounding chassis flow.

## 3. Spacing sequence

Use the following order unless mechanical access makes it impractical:

1. measure and run the prior approximately 3-inch endpoint;
2. run intermediate gaps in a randomized blocked order, with dense coverage
   near contact;
3. reserve 20 mm, or the nearest mechanically available intermediate gap, as
   the held-out validation configuration;
4. return to no-gap and repeat the A2 anchors.

Do not fit the held-out gap until its prospective predictions and errors have
been written. If only discrete slot spacings are available, use every
available layout and identify it by measured clearance rather than assumed
slot pitch.

## 4. Frozen bridge matrix

[`spacing-response-bridge-matrix.csv`](analysis/spacing-response-bridge-matrix.csv)
is the machine-readable design. The companion
[`spacing-response-bridge-matrix.xlsx`](analysis/spacing-response-bridge-matrix.xlsx)
provides filters, definitions, and run-count summaries for operators and
system designers.

The bridge matrix intentionally does not repeat every no-gap cell. At every
retained spacing it includes:

- bottom-only and top-only 400 W isolation with fixed 50/50 fans;
- symmetric 250/250, 400/400, and 500/500 W anchors;
- direction-reversed 600/400 and 400/600 W allocations;
- paired bottom/top 60/40 and 40/60 fixed-fan policies at 400/400 W;
- the deployment-reality 400/400 W automatic-fan condition.

The 0 mm and approximately 76.2 mm endpoints additionally include 250 W
single-card isolation. Every inferential cell requires three admissible
independent replicates. A guarded 600/600 W bump is a safety qualification,
not an inferential replicate; it may create a full cell only after passing the
frozen extension gates.

Existing no-gap evidence may satisfy a bridge cell only when workload,
duration, fan mode, layout, telemetry, and acceptance gates match exactly.
Otherwise it remains contextual evidence rather than being silently pooled.

## 5. Replication and blocking

- Require `n >= 3` admissible independent replicates per retained cell.
- Use three independently initialized blocks, not three adjacent slices from
  one continuous run.
- Balance the order of bottom-heavy and top-heavy conditions across blocks.
- Repeat a 400/400 W, 50/50-fan anchor at the beginning and end of each
  spacing session to estimate within-session drift.
- Do not replace a failed or excluded run without retaining its raw record and
  exclusion reason.
- Promote extra replicates where variance, curvature, thermal proximity, or
  held-out error is high.

## 6. Environmental and telemetry requirements

Transferable spacing claims require synchronized measurements of:

- room and chassis inlet temperature;
- each GPU's local inlet temperature;
- inter-card channel temperature;
- each GPU exhaust temperature;
- chassis fan command/RPM and preferably differential pressure or airflow.

Continue the existing 250 ms GPU/host streams and record, per GPU:

- board power, requested and enforced power limit, utilization;
- graphics/memory clocks and all clock-event reasons/counters;
- temperature, commanded fan percentage, and every physical fan RPM;
- memory use, workload identity, request rate, tokens/s, and latency;
- CPU, NVMe, host-fan, and service/process state.

The primary thermal response is `GPU temperature - local inlet temperature`.
Absolute temperature remains a safety and deployment response. Never divide
temperature by fan percentage; use physical RPM and duty as separate,
potentially nonlinear predictors.

## 7. Preflight, run, and abort gates

Use the frozen V3HOST whole-system reset:

- both GPUs at or below 45 C and 0% utilization;
- CPU Tctl at or below 70 C;
- hottest NVMe at or below 41.9 C;
- all gates held continuously for five minutes;
- exact workload/process isolation verified;
- requested fixed-fan targets within tolerance and automatic restoration
  tested before every manual-fan session.

Standard bridge cells use 120 seconds loaded warmup, 15 minutes measured, and
60 seconds cooldown. Preserve the existing independent telemetry stream.

Abort immediately on:

- any GPU at or above the campaign cutoff;
- fan control loss, fan stall, or actual RPM outside the frozen tolerance;
- workload contamination or loss of intended utilization;
- unexpected power-cap state, hardware thermal slowdown, hardware power
  brake, ECC/Xid event, or telemetry loss;
- environmental sensor failure for a run intended to support transferable
  claims.

Every new high-power/low-fan/layout combination begins with a two-minute bump.
The bump is extended only when the projected steady-state temperature,
temperature slope, fan authority, and all event counters satisfy the frozen
extension rule.

## 8. Prospective model

For card `i`, fit temperature rise above its local inlet as:

`dT_i = R_self,i(gap, rpm_i, layout) * P_i
        + K_below_to_i(gap, rpm_vector, layout) * P_below
        + K_above_to_i(gap, rpm_vector, layout) * P_above
        + block/session effects`.

Use a monotone saturating basis or constrained spline for gap. Estimate
bottom-to-top and top-to-bottom coupling separately. Include power-by-gap,
own-RPM-by-gap, neighbor-RPM-by-gap, layout, ambient/inlet, card identity, and
execution-order interactions. Fit clock, throughput, latency, required RPM,
and remaining thermal/fan margin as linked response surfaces.

Select model complexity using blocked cross-validation. Report:

- held-out-gap MAE and worst error per GPU;
- leave-one-session-out error;
- uncertainty bands and extrapolation flags;
- marginal value of each additional millimeter;
- minimum clearance for each power/fan policy and thermal-margin target;
- power or fan changes required to make a smaller gap emulate a larger one.

Do not publish a smooth curve through unsafe or mechanically unavailable
regions as though it were measured.

## 9. A2 closure and identity control

After the spacing sequence:

1. restore no-gap and repeat 250/250, 400/400, 500/500, 600/400, and 400/600
   anchors under the frozen bridge fan policies;
2. compare A2 against A1 before attributing B-minus-A differences to spacing;
3. at one safe reference gap, physically swap card identities and repeat the
   symmetric 250/400/500 W anchors;
4. include the measured A2 drift and identity effect in uncertainty.

## 10. Stack forecasts

Use the fitted directional gap kernels as adjacency terms in a thermal network
for 3x and 4x stacks. Publish forecasts as bounded and model-based, with
prediction intervals widened for each unvalidated layer. Pairwise
superposition is not assumed valid near fan or pressure limits.

Promotion beyond a bounded forecast requires at least one physical 3-card
stack or an instrumented surrogate heat/flow layer. A 4-card recommendation
requires the 3-card validation error to remain inside the prospective gate and
must state the chassis, spacing, inlet, fan, workload, and power envelope.
