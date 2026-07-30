# 200 W fan-policy crossover

The 200/200 W bottom/top 40/60% and 60/40% cells are internally validated at
`n=3`. Blocks 1 and 2 ran 40/60 first; block 3 deliberately ran 60/40 first.
All six runs held 200 W and 100% GPU utilization, tracked their fixed fan
targets, reached the v2 quantized steady-state plateau, and recorded zero
thermal-slowdown or hardware power-brake events.

## What is supported

The clock redistribution is directionally consistent in all three paired
blocks. Moving the approximately 478 RPM allocation advantage from the top
card to the bottom card reduced bottom mean clock by 2.826-4.870 MHz and
increased top mean clock by 3.001-3.674 MHz. The top-minus-bottom clock gap
therefore moved by +5.827 to +7.964 MHz, while summed clock changed by only
-1.776 to +0.175 MHz. At 200 W, the allocation is primarily redistributing
clock opportunity between cards rather than materially changing aggregate
clock output.

The thermal contrast is not yet separable from execution order. The 60/40
minus 40/60 bottom-temperature delta was -0.738 C, +0.084 C, and -0.974 C
across blocks; the top delta was -0.103 C, +0.479 C, and -0.864 C. The policy
run second tended to inherit warmer session conditions in blocks 2 and 3,
despite a common start gate and five-minute idle soak. This is direct evidence
that session/heat-soak state belongs in the model.

A minimal crossover decomposition estimates a provisional 60/40 policy effect
of -0.651 C bottom and -0.338 C top, plus a later-run effect of +0.324 C bottom
and +0.526 C top. Those are design signals, not publication-grade causal
estimates: only one block used the reversed order, there are no calibrated
local-inlet probes, and no confidence interval is defensible for the
decomposition.

## Consequence for the wider matrix

Future power-cap/fan-policy blocks must randomize or balance order, retain the
preflight soak, and measure local inlet/ambient temperature. Every modeled
power point needs repeated policy pairs rather than isolated runs. This matters
especially at higher powers, where an unmodeled 0.3-0.5 C later-run effect can
be mistaken for a fan-allocation benefit or penalty.

Machine-readable sources:

- [`200w-fan-policy-paired-blocks.csv`](200w-fan-policy-paired-blocks.csv)
- [`200w-fan-policy-order-decomposition.csv`](200w-fan-policy-order-decomposition.csv)
- [`200w-fan-policy-crossover.png`](200w-fan-policy-crossover.png)
