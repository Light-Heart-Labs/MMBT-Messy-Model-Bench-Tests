# 500/500 W automatic-fan replacement R2

This independently initialized 15-minute measured run is internally admissible for `NG-SYM-500`. Both RTX PRO 6000 Blackwell GPUs ran Qwen3.6-27B AWQ-INT4 at 32 concurrent requests per GPU, 100% utilization, and mean board power of 499.990 W (bottom) / 499.986 W (top).

| Position | Mean / max temp | Mean fan / RPM | Mean / last-5m clock | Closing temp / fan slope |
|---|---|---|---|---|
| Bottom GPU0 | 70.059 / 73 C | 42.834% / 1505 RPM | 2513.899 / 2515.365 MHz | +0.0046 C/min / 0.0000 pp/min |
| Top GPU1 | 88.976 / 93 C | 75.606% / 2292 RPM | 2091.610 / 2083.505 MHz | 0.0000 C/min / 0.0000 pp/min |

Both steady-state gates passed. Hardware thermal and power-brake deltas were zero. GPU1 accumulated 0.339487 seconds of software-thermal counter time (0.038% of the measured window), retained as a boundary event rather than evidence of sustained throttling. No calibrated ambient or local-inlet probes were available, so the run is not transferable beyond Tower2's no-gap configuration.

