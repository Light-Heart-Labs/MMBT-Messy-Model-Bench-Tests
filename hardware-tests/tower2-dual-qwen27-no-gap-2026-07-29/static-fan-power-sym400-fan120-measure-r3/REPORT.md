# 400/400 W 120-point fixed-fan measured block R3

- Block: `2026-07-31T19-58-40Z-sym400-fan120-measure-r3`
- Order: B50T70, EQ60, B70T50
- Result: **three passes; three internally admissible R3 cells**

All three cells began after workload isolation, cooldown, and a five-minute
baseline soak. Every GPU exposure held approximately 400 W at 100%
utilization, reached the fixed-quantized steady-state plateau, tracked its
commanded fan duty and physical RPM, and recorded zero thermal-slowdown or
hardware-power-brake events and counter deltas.

For B70T50 minus direction-reversed B50T70, the R3 effects were +0.349 C top
whole-window mean temperature, -0.688 C top last-five-minute temperature,
+5.705 MHz top whole-window mean graphics clock, +20.591 MHz top
last-five-minute graphics clock, and -0.029 seconds top mean request duration.
The closing steady-state temperature and clock effects reproduce R1 and R2.

