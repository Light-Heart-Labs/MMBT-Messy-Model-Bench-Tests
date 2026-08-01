# 350/350 W static fixed-fan qualification

All three pre-registered fixed-fan policies passed their two-minute safety
bumps:

| Policy | Bottom fan / RPM | Top fan / RPM | Bottom mean / max | Top mean / max | Bottom / top clock |
|---|---:|---:|---:|---:|---:|
| EQ50 | 50% / 1,678.6 | 50% / 1,678.7 | 53.678 / 57 C | 66.087 / 71 C | 1,367.9 / 1,280.0 MHz |
| B40T60 | 40% / 1,439.5 | 60% / 1,917.6 | 53.502 / 57 C | 65.620 / 70 C | 1,372.9 / 1,275.6 MHz |
| B60T40 | 60% / 1,917.9 | 40% / 1,439.6 | 52.872 / 56 C | 65.285 / 70 C | 1,364.7 / 1,285.8 MHz |

Every cell held both GPUs at approximately 349.99 W, 100% utilization, and
1.3333 requests/s. Physical fan RPM tracked every fixed target. All sampled
software-thermal, hardware-thermal, and hardware-power-brake events were zero,
and all corresponding counter deltas were zero. Automatic fan control, 600 W
limits, production containers, and user services were restored after each
cell.

The 60/40 lower-biased policy produced the lowest upper-card mean temperature
and highest upper-card mean clock in this short block despite giving the upper
card only 40% local fan. That direction is consistent with the separately
validated lower-neighbor assistance mechanism, but it is not yet an
inferential result: the two-minute cells remained thermally transient, ran
once each, and were deliberately ordered from safer to harsher. Three
15-minute Latin-order blocks are required before comparing policies or fitting
the 350 W power-by-fan interaction.

Artifacts:

- [`350w-static-fan-qualification.csv`](350w-static-fan-qualification.csv)
- [`350w-static-fan-qualification.png`](350w-static-fan-qualification.png)
