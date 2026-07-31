# 400/400 W 120-point fixed-fan measured block R1

- Block: `2026-07-31T15-02-32Z-sym400-fan120-measure-r1`
- Order: EQ60, B70T50, B50T70
- Result: **three passes; three internally admissible R1 cells**

Every cell began after isolation, cooldown, and a five-minute baseline soak.
All six GPU exposures held approximately 400 W at 100% utilization, reached
the fixed-quantized steady-state plateau, tracked commanded fan duty/RPM, and
recorded zero thermal-slowdown or hardware-power-brake events and zero
within-run thermal/brake counter deltas.

R1 is preliminary. The rotated R2/R3 blocks are required before policy
inference or validation at `n=3`.
