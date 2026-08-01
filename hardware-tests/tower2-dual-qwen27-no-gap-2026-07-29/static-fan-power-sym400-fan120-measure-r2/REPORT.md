# 400/400 W 120-point fixed-fan measured block R2

- Block: `2026-07-31T16-47-40Z-sym400-fan120-measure-r2`
- Order: B70T50, B50T70, EQ60
- Result: **three passes; three internally admissible R2 cells**

All three cells began after workload isolation, cooldown, and a five-minute
baseline soak. Every GPU exposure held approximately 400 W at 100%
utilization, reached the fixed-quantized steady-state plateau, tracked its
commanded fan duty and physical RPM, and recorded zero thermal-slowdown or
hardware-power-brake events and counter deltas.

The paired B70T50-minus-B50T70 effect was -0.853 C top mean temperature,
+25.309 MHz top mean graphics clock, and -0.133 seconds top mean request
duration. These directions reproduce R1. R3 remains required before the
400 W effect is promoted to validated status.

