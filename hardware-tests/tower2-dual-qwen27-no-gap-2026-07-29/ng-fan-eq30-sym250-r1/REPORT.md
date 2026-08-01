# Fixed-fan 250/250 W equilibrium cell - replicate 1

- Run: `2026-07-30T03-42-10Z-ng-fan-eq30-sym250-r1`
- Cell: `NG-FAN-EQ30-SYM250`
- Measured window: 10 minutes after 120 seconds of loaded warmup
- Power: 250 W bottom / 250 W top
- Fan policy: both physical fans on each card fixed at 30%
- Workload: Qwen3.6-27B AWQ-INT4, 32 concurrent requests per GPU
- Safety cutoff: 85 C
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.995 W |
| Mean / maximum temperature | 51.281 / 54 C | 67.760 / 73 C |
| Last-five-minute mean temperature | 52.065 C | 70.559 C |
| Mean commanded/current fan | 30.0% / 30.0% | 30.0% / 30.0% |
| Mean physical fan RPM | 1,200.165 | 1,200.176 |
| Mean graphics clock | 807.162 MHz | 775.485 MHz |
| Closing temperature slope | +0.0604 C/min | +0.0582 C/min |
| Completed request rate | 0.9600 req/s | 0.8533 req/s |

All four physical fan streams were complete and tracked their targets with
zero error. Mean card-level RPM differed by only 0.011 RPM. Both GPUs remained
at 100% utilization and at least 95% of their power target for every sample.
No software thermal, hardware thermal, or hardware power-brake event was
observed, and both independent clock telemetry streams agreed with the primary
logger.

At genuinely equal power and equal fan speed, the top card averaged 16.479 C
hotter and 31.677 MHz lower. Its completed-request rate was 11.11% below the
bottom card's rate. The last-five-minute temperatures were 52.065 C bottom and
70.559 C top. Both closing temperature slopes satisfied the preregistered
steady-state gate, so this is the first internally admissible fixed-fan
equilibrium replicate.

The result establishes a Tower2/no-gap positional operating point, not a
transferable chassis coefficient: calibrated ambient and local-inlet probes
were unavailable. Two independent replicates are still required before this
cell reaches the campaign's `n >= 3` validation rule. Automatic fan control,
original services, and 600 W limits were restored after cleanup.
