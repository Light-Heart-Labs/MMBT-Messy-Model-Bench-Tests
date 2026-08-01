# 250 W 2×2 factorial coupling analysis

The two single-card controls and equal 250/250 W cell form a preliminary 2×2 loaded/idle factorial at one power level:

| Cell | GPU0 bottom | GPU1 top |
|---|---|---|
| Bottom only | 250 W Qwen load | Model-resident idle |
| Top only | Isolated idle | 250 W Qwen load |
| Both | 250 W Qwen load | 250 W Qwen load |

There is no full-window both-idle cell, so absolute intercepts are not identified. Matched differences still estimate each card's apparent self-heating and directional neighbor-heating response around this operating point.

## Apparent closed-loop coefficients

These values are changes in GPU core temperature divided by changes in mean board power. They include the GPUs' automatic fan response and are not bare heatsink thermal resistances.

| Effect | First-five-minute estimate | Last-five-minute sensitivity | Interpretation |
|---|---:|---:|---|
| Bottom self-heating | 0.0978°C/W | 0.1009°C/W | Similar across windows |
| Top self-heating | 0.1062°C/W | 0.1027°C/W | Approximately 5–9% higher than bottom |
| Bottom → top coupling | 0.0415°C/W | 0.0471°C/W | Large directional neighbor penalty |
| Top → bottom coupling | -0.0006°C/W | -0.0043°C/W | Not physically negative; indistinguishable from zero |

At 250 W, bottom-to-top coupling is approximately 40–46% as large as the top card's own apparent temperature-per-watt response. The reciprocal top-to-bottom term is not resolved above session variation.

## Direct temperature contrasts

- With the top loaded in both cells, adding the bottom workload raised top temperature by 9.605°C in the first-five-minute comparison and 10.498°C in the last-five-minute comparison.
- With the bottom loaded in both cells, adding the top workload changed bottom temperature by -0.148°C and -0.982°C in the same comparisons. Those small negative values indicate an effect below the uncontrolled measurement noise, not beneficial cooling.
- With both cards loaded equally, the top exceeded the bottom by 15.12°C over the full window and 16.12°C in the last five minutes.

## Model-use boundary

The first-five-minute coefficient set is the cleanest currently available because GPU0 background activity contaminated the latter part of the top-only run. Neither coefficient set is ready for a transferable 3x/4x forecast: external inlet temperatures are absent, cells were sequential rather than randomized, and the top-only cell did not reach the strict steady-state slope criterion.

The next required actions are:

1. stop and restore the identified OpenClaw embedding service as part of isolation;
2. repeat the top-only cell with a longer measured window;
3. repeat the 250 W anchor cells in randomized order;
4. add local inlet probes before fitting ambient-normalized coefficients.

Machine-readable values are in [`250w-factorial-apparent-coefficients.csv`](250w-factorial-apparent-coefficients.csv).
