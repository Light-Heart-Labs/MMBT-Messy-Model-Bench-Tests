# Dual SM120 GPU thermal stress — 500 W for 10 minutes

- Run: `2026-07-29T21-35-09Z-no-gap-both500-10m`
- GPUs: 2× NVIDIA RTX PRO 6000 Blackwell Workstation Edition, compute capability 12.0 (SM120)
- Layout: adjacent cards with no open-slot air gap
- Workload: independent Qwen3.6-27B AWQ-INT4 vLLM engine per GPU
- Load: 32 concurrent requests per GPU
- Power limits: 500 W per GPU
- Warmup / measured / cooldown: 120 s / 600 s / 60 s
- Result: **PASS — no meaningful or sustained thermal throttling**

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean / maximum power | 499.989 / 500.20 W | 499.972 / 500.10 W |
| Mean utilization | 100% | 100% |
| Mean / P95 / maximum temperature | 70.2 / 71 / 74°C | 89.6 / 91 / 93°C |
| Mean / P95 graphics frequency | 2509 / 2527 MHz | 2104 / 2141 MHz |
| First-to-last 5m mean frequency | 2511 → 2507 MHz | 2108 → 2100 MHz |
| Mean / maximum fan | 42.9 / 43% | 78.5 / 83% |
| Software thermal slowdown counter | 0 s | 1.054393 s |
| Hardware thermal slowdown | 0 | 0 |
| Hardware power brake | 0 | 0 |

**Thermal-throttling verdict:** No meaningful or sustained thermal throttling occurred. GPU1/top’s before/after NVIDIA counter recorded 1.054393 seconds of software thermal slowdown—only 0.176% of the 10-minute measured window—but no 1 Hz sample caught the state active, both GPUs sustained approximately 500 W and 100% utilization, hardware thermal and power-brake counters remained zero, and GPU1’s first-to-last five-minute mean frequency changed by only -0.37%. GPU1 clearly operated close to its thermal-management boundary at 89.6°C mean, 93°C maximum, and up to 83% fan, but the isolated one-second counter increment is noise-level evidence rather than an operational throttling problem.

All 1,888 recorded requests completed successfully with HTTP 200. Original services and 600 W power limits were restored after the test.
