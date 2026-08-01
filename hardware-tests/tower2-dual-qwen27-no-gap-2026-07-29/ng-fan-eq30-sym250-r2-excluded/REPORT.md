# Fixed-fan 250/250 W cell - replicate 2 excluded

- Run: `2026-07-30T04-05-46Z-ng-fan-eq30-sym250-r2`
- Cell: `NG-FAN-EQ30-SYM250`
- Measured window: 10 minutes after 120 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: both physical fans on each card fixed at 30%
- Result: **excluded; GPU1/top did not satisfy the steady-state gate**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.994 W |
| Mean / maximum temperature | 51.063 / 54 C | 67.471 / 73 C |
| Mean physical fan RPM | 1,200.175 | 1,200.177 |
| Mean graphics clock | 807.891 MHz | 776.814 MHz |
| Closing temperature slope | +0.0056 C/min | +0.4288 C/min |
| Completed request rate | 0.9600 req/s | 0.8533 req/s |

Power, utilization, workload isolation, fan telemetry, and fan-target tracking
all passed. All four fans held 30% at approximately 1,200 RPM and card-level
mean RPM differed by only 0.002 RPM. No software thermal, hardware thermal, or
hardware power-brake event occurred.

The top-minus-bottom mean temperature difference was 16.408 C and the mean
graphics-clock difference was -31.077 MHz. Those values closely reproduce R1's
16.479 C and -31.677 MHz results, and throughput was identical to R1 on both
GPUs. Nevertheless, the top closing temperature slope was +0.4288 C/min,
exceeding the preregistered absolute 0.1 C/min steady-state threshold.
Therefore this run is published as repeatability and transient evidence but
does not count toward the campaign's `n >= 3` validation requirement.

The strict slope outcome is sensitive to the integer-degree GPU temperature
channel. That limitation should be addressed prospectively with longer
measured windows or a preregistered quantization-aware plateau test, not by
reclassifying this run after seeing its result.
