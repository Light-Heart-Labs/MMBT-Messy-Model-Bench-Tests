# 300 W V3HOST fan-policy crossover - block 2

Block 2 reversed the order used in block 1: bottom/top 40/60 ran first,
followed by 60/40. Both runs used identical 300/300 W caps, Qwen workload,
combined fan command, whole-system reset gates, warmup, measured duration, and
telemetry.

The final ready samples differed by 0/0 C on GPU0/GPU1, 1.2 C on CPU Tctl,
and 0 C on hottest NVMe. Loaded CPU and hottest-NVMe means differed by only
-0.197 and -0.698 C. The block satisfies the prospective tightly matched start
tolerances.

## Matched policy effect

The table reports 60/40 minus 40/60:

| Response | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Fan RPM | +477.988 | -478.032 |
| Mean temperature | -0.777 C | -0.508 C |
| Last-five-minute temperature | -0.935 C | -0.416 C |
| Mean graphics clock | -6.785 MHz | +5.962 MHz |
| Last-five-minute graphics clock | -6.133 MHz | +6.158 MHz |
| Mean request duration | +0.123 s | -0.154 s |
| Request rate | 0.0000 req/s | 0.0000 req/s |

Combined mean graphics clock changed by -0.823 MHz (-0.041%); combined
last-five-minute clock changed by +0.025 MHz. Aggregate request rate was
identical. The allocation therefore redistributed card-level performance
without a meaningful change in combined clock or coarse throughput.

## Engineering interpretation

Moving approximately 478 RPM of fan effort from the top card to the bottom
card cooled **both** GPUs. That supports the hypothesis that the lower card's
fans contribute more effectively to shared through-stack airflow than the
upper card's fans in the no-gap layout.

At the same time, the bottom card became cooler but lost one graphics-clock
bin, while the top became cooler and gained roughly one bin. Local temperature
cannot explain the bottom clock loss. The direction is consistent with a small
local fan-power tax inside the capped board-power envelope, combined with
shared airflow. It is not yet proof of electrical fan inclusion because fan
power was not independently metered; the planned own-fan, neighbor-fan, and
power-headroom isolation sweeps remain necessary.

The latency changes follow the clock transfer: the bottom's mean request
duration increased 0.123 seconds while the top's fell 0.154 seconds. This is a
per-card load-balancing effect, not a demonstrated aggregate-throughput gain.

Block 3 and `n>=3` per policy are still required before promoting these values
to validated 300 W coefficients.

Machine-readable source:
[`300w-v3host-fan-policy-block2.csv`](300w-v3host-fan-policy-block2.csv).
