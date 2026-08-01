# 500/500 W automatic-fan replacement R3

This independently initialized 15-minute measured run is internally admissible for `NG-SYM-500`. Both GPUs sustained 100% utilization and mean board power of 499.990 W (bottom) / 499.984 W (top).

| Position | Mean / max temp | Mean fan / RPM | Mean / last-5m clock | Closing temp / fan slope |
|---|---|---|---|---|
| Bottom GPU0 | 70.159 / 73 C | 42.941% / 1512 RPM | 2510.574 / 2510.618 MHz | +0.0606 C/min / 0.0000 pp/min |
| Top GPU1 | 89.098 / 92 C | 77.215% / 2331 RPM | 2077.341 / 2066.734 MHz | -0.0015 C/min / 0.0000 pp/min |

Both steady-state gates passed. Hardware thermal and power-brake deltas were zero. GPU1 accumulated 0.680029 seconds of software-thermal counter time (0.076%). The run is internally useful but not transferable because calibrated ambient and per-card inlet measurements were unavailable.

