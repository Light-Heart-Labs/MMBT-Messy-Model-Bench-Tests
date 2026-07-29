# Tower2 no-gap dual-GPU 600 W stress — safety abort

- Run: `2026-07-29T21-58-23Z-no-gap-both600-30m`
- Requested window: 30 minutes measured at 600 W per GPU
- Actual measured exposure: approximately 5 minutes
- Layout: adjacent cards with no open-slot air gap
- Workload: independent Qwen3.6-27B AWQ-INT4 vLLM engine per GPU, 32 concurrent requests each
- Emergency cutoff: 96°C
- Result: **ABORTED — confirmed GPU1/top thermal throttling**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean / minimum board power | 599.98 / 598.07 W | 589.73 / 540.59 W |
| Samples at or above 570 W | 100% | 97.23% |
| Mean / maximum temperature | 74.97 / 77°C | 92.65 / 96°C |
| Mean / minimum graphics clock | 2739 / 2235 MHz | 2559 / 1957 MHz |
| Mean / maximum fan | 45.6 / 46% | 99.4 / 100% |
| Mean utilization | 100% | 100% |
| Software-thermal active samples | 0 | 9 |
| Software thermal slowdown counter | 0 s | 5.840209 s |
| Hardware thermal slowdown counter | 0 s | 0.280003 s |
| Hardware power-brake samples | 0 | 0 |

GPU1/top could not sustain the requested 600 W in the adjacent-card layout. It reached 100% fan almost immediately, settled near 93°C, repeatedly fell into the 580–592 W range, and showed clock excursions below 2.0 GHz. At the cutoff sample it reached 96°C, drew 554.33 W average / 535.25 W instantaneous, ran at 2.13 GHz, and reported the software-thermal flag active. The before/after counters also recorded both software and hardware thermal slowdown. The safety runner stopped the test as designed; increasing the cutoff would not convert this into a clean 600 W result and is not recommended.

All 960 completed requests returned HTTP 200 before the abort. Original services and 600 W power limits were restored, the temporary GPU0 container was removed, Sanctuary queues returned to zero, and both GPUs returned to 0% utilization.
