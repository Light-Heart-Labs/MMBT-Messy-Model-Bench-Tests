# Fan-aware interpretation of the no-gap results

> New fixed-fan result: the first matched-total-RPM crossed-policy triplet is
> documented in
> [`CROSSED_FAN_POLICY_PRELIMINARY.md`](CROSSED_FAN_POLICY_PRELIMINARY.md).
> At `n=1`, bottom/top 70/30% cooled both cards relative to 50/50 and the exact
> reverse 30/70 allocation, while producing the smallest inter-card clock gap.

## Scope

Every completed standard load cell before the new fixed-fan bump used NVIDIA's
stock automatic fan controller. Those data therefore describe **closed-loop
operating points**:

```text
power + inlet conditions + layout -> temperature -> fan command -> temperature
```

They do not identify a position-only thermal resistance at equal airflow. The
raw source table is
[`auto-fan-operating-points.csv`](auto-fan-operating-points.csv).

The campaign has now completed fixed-fan safety bumps and its first steady
fixed-fan equilibrium replicate. Fixed-fan results are tracked separately in
[`fan-controlled-operating-points.csv`](fan-controlled-operating-points.csv)
so transient control checks cannot be mistaken for steady automatic-controller
cells.

## First fixed-fan evidence

`NG-FAN-EQ30-SYM250-BUMP` R2 held both GPUs at 250 W/100% utilization while all
four physical fans remained at exactly 30% and approximately 1,201 RPM. Across
the two-minute measured window:

| Metric | Bottom | Top |
|---|---:|---:|
| Mean / maximum temperature | 48.116 / 51°C | 57.321 / 64°C |
| End-of-window temperature | 50°C | 63°C |
| Closing temperature slope | +2.8106°C/min | +6.1990°C/min |
| Mean graphics clock | 814.911 MHz | 802.017 MHz |

The top averaged 9.205°C hotter and ended 13°C hotter under genuinely equal fan
duty and RPM. This is the first direct observation with controller response
removed, but it is not an equilibrium coefficient: both cards—especially the
top—were still warming quickly. Its value is proof of independent control,
RPM measurement, directional divergence, safety cutoff operation, and
automatic restoration. A longer guarded exposure is required to find the
30/30% equilibrium or its safe boundary.

The five-minute R3 extension reproduced the trajectory and remained safe. At
effectively identical 1,201 RPM mean fan speed, bottom/top mean temperatures
were 49.675/62.276°C, maxima were 54/70°C, and the observed closing gap reached
17°C. The closing slopes fell to +0.7606/+2.1283°C/min, proving the initial
rise was bending but not yet equilibrated. The transient closing gap already
exceeded the roughly 15°C mean gap in the automatic-controller 250/250 runs,
consistent with the top card's extra automatic fan effort masking some of its
burden. Because one figure is a transient endpoint and the other a 10-minute
mean, this is not yet a like-for-like equilibrium comparison.

The guarded ten-minute `NG-FAN-EQ30-SYM250` R1 extension resolved that
comparison. Bottom and top closing temperature slopes were +0.0604 and
+0.0582 C/min, satisfying the steady-state gate. At the same 250 W board
power and the same 30% / approximately 1,200 RPM fan speed, the bottom averaged
51.281 C and the top 67.760 C, a 16.479 C mean positional delta. The top
averaged 31.677 MHz lower and delivered 0.8533 requests/s versus 0.9600
requests/s on the bottom, with all explicit thermal and brake counters at
zero. This demonstrates heat-associated boost/performance loss below the
driver's formal thermal-throttling thresholds. It is the first admissible
replicate, not yet a validated coefficient; two repeats and calibrated
ambient/local-inlet measurements are still needed.

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

The original fixed-fan test failed because the installed 510
`nvidia-settings` client did not match the active 595.58.03 driver. A matching
client successfully commanded and restored both physical fans on the idle
bottom card, and the matched package is now installed. Beginning with the next
admissible run, all four physical fan RPMs are logged at 1 Hz. Fixed-fan loaded
cells can now proceed through the required bump-test sequence.
