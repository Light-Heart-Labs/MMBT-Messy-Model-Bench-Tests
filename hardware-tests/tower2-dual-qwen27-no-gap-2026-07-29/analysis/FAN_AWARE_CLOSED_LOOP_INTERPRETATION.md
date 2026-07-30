# Fan-aware interpretation of the no-gap results

## Scope

Every completed load cell so far used NVIDIA's stock automatic fan controller.
These data therefore describe **closed-loop operating points**:

```text
power + inlet conditions + layout -> temperature -> fan command -> temperature
```

They do not identify a position-only thermal resistance at equal airflow. The
raw source table is
[`auto-fan-operating-points.csv`](auto-fan-operating-points.csv).

## What is established now

### The 250/250 W result is repeatable as a complete operating point

The pilot and clean replicate agree closely:

| Run | Bottom temperature / fan | Top temperature / fan | Top-minus-bottom |
|---|---:|---:|---:|
| Pilot | 51.849°C / 30.673% | 66.969°C / 40.146% | +15.120°C / +9.473 pp |
| Clean R2 | 52.730°C / 31.212% | 67.613°C / 40.470% | +14.883°C / +9.258 pp |

This is strong evidence that the top position demands materially more cooling
under the stock controller at equal 250 W. It is not yet an `n >= 3`
fan-normalized coefficient.

### Fan response hides part of the positional burden

At 250/250 W, the top card is about 15°C hotter **after** its controller has
already increased fan duty by about 9.4 percentage points. Holding both cards
at the bottom card's fan speed could increase the temperature gap. Holding both
at a much higher fan speed could reduce it. Neither counterfactual can be
computed from these automatic-fan runs alone.

At 500/500 W, the top card averaged 89.568°C at 78.544% fan while the bottom
averaged 70.198°C at 42.909% fan. The top still ran 19.370°C hotter despite
35.635 percentage points more commanded cooling. This is a strong stock-system
constraint, not a constant thermal-resistance estimate.

The aborted 600/600 W cell is the clearest example of controller compression.
The top fan averaged 99.4%, leaving effectively no remaining fan authority, yet
the top averaged 17.68°C hotter, reached 96°C, lost board power, and accumulated
software and hardware thermal-slowdown time. A raw temperature delta without
the accompanying fan state would substantially understate the severity.

### Power allocation has immediate design value

At 600 W bottom / 400 W top, the top card still averaged 7.353°C hotter and
required 17.982 additional fan percentage points despite consuming about
200 W less. Nevertheless, that allocation completed 30 minutes without thermal
counter growth, whereas 600/600 W failed in about five minutes. This is direct
evidence that power placement—not only total stack power—matters in a no-gap
stack.

### Directional coupling is real

With only the bottom card loaded at 250 W, the model-resident idle top card
averaged 44.266°C at approximately 22.5 W. Across three admissible reverse
isolations, loading only the top card left the idle bottom near 29°C. The
asymmetry is consistent with strong bottom-to-top heat transport and little
resolvable top-to-bottom penalty in this chassis. Environmental probes and
additional bottom-only replicates are still required before treating the
preliminary coupling coefficient as transferable.

## Present value of the campaign

The current evidence is already useful for:

- establishing unsafe and workable Tower2 no-gap operating envelopes;
- choosing asymmetric power allocations;
- estimating stock-controller fan demand, noise burden, and remaining fan
  authority;
- detecting a directional neighbor-heating path;
- identifying thermal-history contamination and enforcing repeatability;
- defining where a stack forecast must become conservative.

It is not yet sufficient for:

- predicting the temperature delta at equal 30%, 50%, 70%, or 85% fan;
- converting fan percentage or RPM into CFM through the obstructed stack;
- separating local hot-air ingestion from heatsink/self-heating resistance;
- transferring coefficients to another chassis;
- validating a three- or four-card forecast.

In short, this is a strong operational-envelope dataset and an improving
identification campaign—not yet a finished universal cooling model.

## Required fan-aware model

For temperature rise above each card's measured local inlet:

```text
theta_bottom =
    R_bb(F_bottom, F_top) * P_bottom
  + R_bt(F_bottom, F_top) * P_top

theta_top =
    R_tt(F_top, F_bottom) * P_top
  + R_tb(F_top, F_bottom) * P_bottom
```

`F` must include actual RPM and later measured flow/pressure, not merely the
reported percentage. Cross-fan terms are required because one card's fans may
assist, starve, or disturb the other card.

Two complementary output models should be published:

1. **Automatic-controller model:** predicts the temperature, fan demand,
   clocks, and throughput a deployed stock system will produce.
2. **Fixed-airflow model:** predicts intrinsic self/cross heating at controlled
   fan RPM and measured local inlet conditions.

The fixed-fan matrix is currently gated by Tower2's X-server configuration:
NV-CONTROL fan target assignments fail even though duty and RPM are readable.
Enabling and validating that capability requires a maintenance window for an
X configuration change/restart. Beginning with the next admissible run, all
four physical fan RPMs are logged at 1 Hz so the automatic-controller model can
advance immediately.
