# Bounded 3x/4x stack-height planning envelope v1

This artifact turns the validated no-gap two-card anchors into explicit
planning scenarios for three- and four-card stacks. It is deliberately not a
single-point prediction.

For each power level, the two-card equal-fan population supplies the observed
bottom temperature, top temperature, and positional gap. Two scenarios bracket
the unknown additional-card behavior:

1. **Optimistic containment:** extra cards add no top-card penalty beyond the
   observed two-card top temperature.
2. **Additive interfaces:** every added card-to-card interface repeats the
   observed two-card positional gap.

The additive edge is a transparent engineering scenario, not a guaranteed
worst case; recirculation could make a real chassis worse, while strong
through-flow could make it better.

| Power/GPU | Validated 2x top | 3x top scenario range | 4x top scenario range | Equal-fan policy |
|---:|---:|---:|---:|---|
| 250 W | 57.72 C | 57.72--69.01 C | 57.72--80.30 C | 50/50, 100-point budget |
| 350 W | 70.87 C | 70.87--86.36 C | 70.87--101.85 C | 50/50, 100-point budget |
| 400 W | 77.06 C | 77.06--92.45 C | 77.06--107.84 C | 60/60, 120-point budget |

The 350 and 400 W additive four-card scenarios exceed 100 C, and the 400 W
three-card scenario approaches the cards' reported 93 C thermal limit. This
does not prove those stacks will reach those temperatures. It does prove that
assuming two-card temperatures remain unchanged is not a safe server-design
basis.

## Fan-coordination scenario

The validated direction-reversed two-card experiments provide a second
planning range. For unmeasured 3x/4x stacks, coordinated lower-card fan support
is assigned a recovery range from zero to the two-card effect multiplied by
the number of lower interfaces:

| Power/GPU | Validated 2x recovery | 3x scenario recovery | 4x scenario recovery |
|---:|---:|---:|---:|
| 250 W | 0.570 C / 5.084 MHz | 0--1.141 C / 0--10.167 MHz | 0--1.711 C / 0--15.251 MHz |
| 350 W | 0.652 C / 14.005 MHz | 0--1.304 C / 0--28.009 MHz | 0--1.956 C / 0--42.014 MHz |
| 400 W | 0.876 C / 22.874 MHz | 0--1.753 C / 0--45.747 MHz | 0--2.629 C / 0--68.621 MHz |

The recovery multiplier is also a scenario, not a causal extrapolation. Only
the two-card values are measured. A real four-card flow path may saturate,
compound, reverse locally, or be dominated by chassis pressure and inlet
temperature.

## Required validation to tighten the envelope

- Repeat the 250/350/400 W anchors with a physical gap to identify spacing
  response.
- Measure calibrated ambient and each card's local inlet temperature.
- Swap card positions to separate card identity from vertical position.
- Validate at least one three-card or four-card stack at low power before
  raising caps.
- Test the stack-aware fan service against matched static policies and verify
  fail-safe restoration.

Artifacts:

- [`stack-height-planning-envelope-v1.csv`](stack-height-planning-envelope-v1.csv)
- [`stack-height-planning-envelope-v1.png`](stack-height-planning-envelope-v1.png)
- [`plot-stack-height-planning-envelope-v1.py`](plot-stack-height-planning-envelope-v1.py)

