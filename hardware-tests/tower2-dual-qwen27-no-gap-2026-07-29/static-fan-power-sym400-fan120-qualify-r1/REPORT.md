# 400/400 W 120-point fixed-fan qualification block

- Block: `2026-07-31T13-49-10Z-sym400-fan120-qualify-r1`
- Mode: qualification
- Order: EQ60, B50T70, B70T50
- Result: **all three safety bumps passed**

Each cell began after the full isolation, cooldown, and five-minute baseline
soak. Both cards then held approximately 400 W at 100% utilization for the
120-second measured window. Commanded fan duty and physical RPM were logged
per GPU, and all policies had zero thermal-slowdown or hardware-power-brake
events and zero within-run thermal/brake counter deltas.

These results qualify the 120-point policies for the pre-registered
15-minute Latin-order blocks. They are non-steady safety screens and do not
count toward the validation sample size.
