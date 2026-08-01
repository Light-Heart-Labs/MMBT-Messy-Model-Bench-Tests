# Cross-power fan-allocation evidence map

This synthesis compares the direction-reversed fixed-fan experiments already
completed at 200, 250, 300, 350, and 400 W per GPU. The contrast always moves
20 fan-duty points from the upper card to the lower card while keeping total
commanded duty fixed. At 200--350 W the budget is 100 points (60/40 versus
40/60); the safety-amended 400 W study uses 120 points (70/50 versus 50/70).

| Power | Evidence | Upper-GPU temperature effect | Upper-GPU clock effect | Upper-GPU latency effect |
|---:|---|---:|---:|---:|
| 200 W | Provisional, order-confounded | -0.163 C mean | +3.256 MHz mean | not available |
| 250 W | Validated paired `n=3` | **-0.570 C mean** | **+5.084 MHz mean** | not available |
| 300 W | `n=3` populations, only two causally matched blocks | -0.146 C mean; not robust | +5.556 MHz mean | -0.172 s mean |
| 350 W | Validated paired `n=3` | **-0.652 C mean** | **+14.005 MHz mean** | **-0.133 s mean** |
| 400 W | Validated paired `n=3`, 120-point budget | **-0.876 C last 5m** | **+22.874 MHz last 5m** | -0.090 s whole-window |

Negative temperature and latency and positive clock are improvements for the
upper card under the lower-biased allocation.

## What is now defensible

The no-gap stack has reproducible cross-card airflow coupling. At 250, 350,
and 400 W, allocating more of a fixed fan budget to the lower card improves a
measured upper-card thermal or performance response even though the upper card
receives less local fan duty. The effect is not merely fan-command noise:
physical RPM tracking is exact, and the direction-reversed policies have
near-identical total RPM.

The performance value grows materially across the validated power anchors:
about +5 MHz upper-card mean clock at 250 W, +14 MHz at 350 W, and +22.9 MHz
closing clock at 400 W. This supports a qualitative power-by-stack-airflow
interaction: system-level fan coordination matters more as heat density rises.

## What is not defensible

A single continuous coefficient must not be fit across all five points. The
200 W estimate retains execution-order confounding; the 300 W causal contrast
has only two closely matched blocks and did not reproduce a robust thermal
effect; and the 400 W safety envelope required a larger 120-point fan budget.
The response also mixes whole-window and closing steady-state estimands where
older runs lack the newer last-five-minute fields.

Accordingly, the current 3x/4x model may use these results only as bounded
directional priors: lower cards should receive nonzero assistance when upper
cards heat up, and that assistance should increase with stack heat density.
It may not multiply the two-card temperature or clock coefficient by stack
height. Quantitative 3x/4x coefficients still require either physical stacks
or calibrated inlet/ambient measurements plus spacing/swap validation.

Artifacts:

- [`cross-power-fan-allocation-evidence.csv`](cross-power-fan-allocation-evidence.csv)
- [`cross-power-fan-allocation-evidence.png`](cross-power-fan-allocation-evidence.png)
- [`plot-cross-power-fan-allocation-evidence.py`](plot-cross-power-fan-allocation-evidence.py)

