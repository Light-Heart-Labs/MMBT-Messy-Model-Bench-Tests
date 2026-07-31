# 400/400 W static fixed-fan qualification

All three pre-registered matched-budget policies passed their two-minute
safety bumps:

| Policy | Bottom fan / RPM | Top fan / RPM | Bottom mean / max | Top mean / max | Bottom / top clock |
|---|---:|---:|---:|---:|---:|
| EQ50 | 50% / 1,678.8 | 50% / 1,678.7 | 57.965 / 62 C | 71.588 / 76 C | 1,801.7 / 1,606.8 MHz |
| B40T60 | 40% / 1,439.7 | 60% / 1,917.7 | 58.023 / 62 C | 71.491 / 76 C | 1,797.9 / 1,607.1 MHz |
| B60T40 | 60% / 1,917.7 | 40% / 1,439.5 | 57.318 / 60 C | 71.165 / 77 C | 1,792.5 / 1,621.3 MHz |

Every cell held both GPUs at approximately 399.99 W and 100% utilization.
Physical fan RPM tracked every fixed target, workload isolation passed, and
all software-thermal, hardware-thermal, and hardware-power-brake events and
counter deltas were zero. Automatic fan control, 600 W power limits, and
production containers were restored after each cell.

The lowest-top-fan B60T40 case peaked at 77 C, leaving a 19 C safety margin to
the test cutoff. Short-window mean values are still affected by warm-up and
execution order and must not be treated as policy effects. The block clears
all three policies for independently initialized 15-minute Latin-order runs.

Artifacts:

- [`400w-static-fan-qualification.csv`](400w-static-fan-qualification.csv)
- [`400w-static-fan-qualification.png`](400w-static-fan-qualification.png)
