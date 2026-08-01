# 500/500 W automatic-fan R5 — excluded controller-hunting observation

This conservative replacement used a 604-second idle soak ending at 29 C / 32 C and a 20-minute measured window. It completed safely at 500 W and 100% utilization on both GPUs, but is excluded because GPU1/top's closing automatic-fan slope was -0.4931 percentage points/minute against the v1 limit of 0.2. GPU1 temperature was effectively flat at +0.0098 C/min, showing late fan-controller hunting rather than ongoing thermal rise.

Mean temperatures were 70.747 C bottom and 89.215 C top; mean fans were 43.141% / 1517 RPM and 79.270% / 2380 RPM. Last-five-minute temperatures were 70.947 C and 89.296 C. Hardware thermal and power-brake deltas were zero. GPU1 software-thermal counter growth was 0.577553 seconds (0.048%). This run is retained as evidence that strict monotonic fan-slope gates can reject an otherwise stable high-power automatic-fan operating point.

