# 300 W V3HOST fan-policy crossover - block 3

Block 3 ran bottom/top 60/40 followed by 40/60. Both runs used identical
300/300 W caps, Qwen workload, combined fan command, whole-system reset gates,
warmup, measured duration, and telemetry.

The final ready samples differed by +1/0 C on GPU0/GPU1, +0.9 C on CPU Tctl,
and 0 C on hottest NVMe. Loaded CPU and hottest-NVMe means differed by +0.907
and -0.149 C. The block satisfies the prospective tightly matched tolerances.

## Matched policy effect

The table reports 60/40 minus 40/60:

| Response | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Fan RPM | +478.006 | -478.017 |
| Mean temperature | -0.011 C | +0.216 C |
| Last-five-minute temperature | -0.082 C | +0.328 C |
| Mean graphics clock | -8.932 MHz | +5.150 MHz |
| Last-five-minute graphics clock | -10.719 MHz | +4.380 MHz |
| Mean request duration | +0.146 s | -0.190 s |
| Request rate | 0.0000 req/s | 0.0000 req/s |

Combined mean graphics clock changed by -3.782 MHz and combined
last-five-minute clock by -6.339 MHz. Aggregate request rate was identical.

## Interpretation

Unlike block 2, block 3 does not show a meaningful cooling advantage from
moving fan effort to the bottom card. The temperature changes are near the
1 C sensor quantization scale and slightly warm the top card. It does repeat
the card-level clock and latency transfer: more local fan RPM accompanies
lower local clock and longer request duration, while the other card moves in
the opposite direction. This supports a small local fan-power or control-state
effect, but not a combined-throughput benefit.

Machine-readable source:
[`300w-v3host-fan-policy-block3.csv`](300w-v3host-fan-policy-block3.csv).
