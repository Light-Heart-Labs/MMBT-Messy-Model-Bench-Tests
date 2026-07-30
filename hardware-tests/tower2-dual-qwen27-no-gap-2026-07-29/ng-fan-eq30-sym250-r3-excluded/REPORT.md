# Fixed-fan 250/250 W cell - replicate 3 excluded

- Run: `2026-07-30T04-29-55Z-ng-fan-eq30-sym250-r3`
- Cell: `NG-FAN-EQ30-SYM250`
- Measured window: 10 minutes after 120 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: both physical fans on each card fixed at 30%
- Result: **excluded; GPU1/top did not satisfy the steady-state gate**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.994 W |
| Mean / maximum temperature | 51.258 / 54 C | 67.681 / 73 C |
| Mean physical fan RPM | 1,200.177 | 1,200.177 |
| Mean graphics clock | 807.326 MHz | 774.744 MHz |
| Closing temperature slope | +0.0119 C/min | +0.2186 C/min |
| Completed request rate | 0.9600 req/s | 0.8533 req/s |

Power, utilization, workload isolation, fan telemetry, and fan-target tracking
all passed. Mean card-level RPM was identical to three decimal places. No
software thermal, hardware thermal, or hardware power-brake event occurred.

The top-minus-bottom mean temperature difference was 16.423 C and the mean
graphics-clock difference was -32.582 MHz. Together, R1 through R3 span only
16.408 to 16.479 C in temperature delta and reproduce identical request rates.
Nevertheless, the top closing temperature slope was +0.2186 C/min, exceeding
the preregistered absolute 0.1 C/min threshold. This run is therefore excluded
from formal validation.

The three-run comparison shows that a three-minute linear regression against
an integer-degree sensor is too quantization-sensitive for this low-slope
plateau. The protocol should be revised prospectively for new cell IDs using a
longer observation window and a quantization-aware plateau test. R2 and R3
remain excluded under the rule in force when they ran.
