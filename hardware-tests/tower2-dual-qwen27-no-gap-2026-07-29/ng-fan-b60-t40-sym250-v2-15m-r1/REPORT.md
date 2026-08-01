# Fixed-fan 250/250 W, bottom/top 60/40% - v2 replicate 1

- Run: `2026-07-30T09-22-35Z-ng-fan-b60-t40-sym250-v2-15m-r1`
- Cell: `NG-FAN-B60-T40-SYM250-V2-15M`
- Measured window: 15 minutes after 120 seconds of loaded warmup
- Result: **pass; internally admissible replicate 1 of 3**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.991 W | 249.995 W |
| Mean / maximum temperature | 45.915 / 48 C | 57.283 / 60 C |
| Last-five-minute mean temperature | 46.042 C | 58.033 C |
| Mean physical fan RPM | 1,917.109 | 1,439.133 |
| Mean graphics clock | 808.035 MHz | 801.203 MHz |
| Last-five-minute mean clock | 807.547 MHz | 798.764 MHz |
| Completed request rate | 0.9956 req/s | 0.9244 req/s |
| V2 one-minute medians | 46, 46, 46, 46, 46 C | 58, 58, 58, 58, 58 C |

All v2 gates passed with zero slowdown/brake events. Total mean card-level fan
speed was 3,356.242 RPM, only 0.021 RPM below the validated 50/50 policy mean.

This was a prospective check of the committed piecewise-linear 60/40
prediction. Observed minus predicted errors were -0.038/+0.275 C for
bottom/top temperature and +0.551/+1.326 MHz for bottom/top mean clock.

GPU0 recorded two consecutive 250 ms samples at the measured-phase boundary
with 2,362 MHz graphics clock, 240.90 W averaged power, and 330.28 W
instantaneous power. The independent NVML log confirms the samples. They are
retained as real sub-second phase-transition excursions rather than silently
filtered. Excluding only those two greater-than-1.2 GHz points gives a
descriptive GPU0 clock mean of approximately 807.17 MHz; the unaffected
last-five-minute mean is 807.55 MHz. The run remains admissible, but clock-model
validation should use all three replicates and report robust sensitivity.
