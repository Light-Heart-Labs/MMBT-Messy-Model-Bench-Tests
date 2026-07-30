# Fixed-fan 250/250 W, bottom/top 40/60% - v2 replicate 2

- Run: `2026-07-30T11-21-26Z-ng-fan-b40-t60-sym250-v2-15m-r2`
- Cell: `NG-FAN-B40-T60-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 2 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.995 W | 249.994 W |
| Mean / maximum temperature | 46.697 / 49 C | 57.853 / 61 C |
| Last-five-minute mean temperature | 47.035 C | 58.983 C |
| Mean physical fan RPM | 1,439.083 | 1,917.121 |
| Mean graphics clock | 814.416 MHz | 795.596 MHz |
| Last-five-minute mean clock | 813.545 MHz | 793.901 MHz |
| Completed request rate | 0.9944 req/s | 0.8889 req/s |
| V2 one-minute medians | 47, 47, 47, 47, 47 C | 59, 59, 59, 59, 59 C |

All v2 gates passed with zero slowdown/brake events. Total mean card-level fan
speed was 3,356.204 RPM, within 0.059 RPM of the validated 50/50 policy mean.
Fan duty tracked the commanded 40/60% policy without error for the complete
measured window.

R2 reproduced R1 within +0.018/+0.046 C for bottom/top mean temperature and
-0.171/+0.651 MHz for mean clock. The 18.820 MHz top-minus-bottom mean clock
deficit and 11.156 C positional temperature delta also repeated. Independent
randomized NVML clock telemetry agreed with the primary mean clocks within
0.016%.

This is the second internally admissible replicate. A third independently
initialized run is required before updating the frozen fan-allocation model
with this knot or promoting the 40/60 comparisons to validated findings.
