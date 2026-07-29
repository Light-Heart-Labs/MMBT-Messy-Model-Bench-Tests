# Tower2 no-gap dual-GPU bump — bottom 600 W / top 400 W

- Run: `2026-07-29T20-38-12Z-no-gap-bottom600-top400-2m`
- Physical configuration: GPU1/top directly above GPU0/bottom with no open-slot air gap
- Workload: one Qwen3.6-27B AWQ-INT4 vLLM engine per GPU
- Load: 32 concurrent chat-completion workers per GPU
- Warmup / measured / cooldown: 60 s / 120 s / 60 s
- Power caps: GPU0/bottom 600 W; GPU1/top 400 W
- Emergency cutoff: 96°C
- Result: **PASS**

## Measured results

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 600.001 W | 399.990 W |
| Mean utilization | 100% | 100% |
| Mean temperature | 76.25°C | 76.58°C |
| P95 temperature | 80°C | 84°C |
| Maximum temperature | 80°C | 87°C |
| Mean graphics clock | 2748 MHz | 1554 MHz |
| Mean fan speed | 45.4% | 45.2% |
| Maximum fan speed | 48% | 51% |
| Hardware thermal slowdown | None | None |
| Software thermal slowdown | None | None |
| Hardware power brake | None | None |

The top card consumed 200 W less but still ran 0.33°C hotter on average, 4°C hotter at P95, and 7°C hotter at the observed maximum. It began the measured window cooler than the bottom card, then crossed over and finished at 85°C while the bottom card finished at 80°C. This is a strong transient indication of restricted intake and/or heat transfer from the lower card.

The test is only a two-minute bump and did not establish steady-state thermal equilibrium. A longer matched cell is required before estimating a thermal-coupling coefficient.

## Request and host results

- Bottom GPU0: 224 completed requests, all HTTP 200; mean latency 19.98 s.
- Top GPU1: 192 completed requests, all HTTP 200; mean latency 22.66 s.
- CPU Tctl: 82.67°C mean, 87.9°C maximum.
- Maximum CCD temperature: 73.16°C mean, 86.2°C maximum.
- NVMe temperature: 40.9°C maximum.

## Cleanup verification

- Original 600 W power limits restored on both GPUs.
- Temporary GPU0 vLLM container removed.
- Sanctuary returned to 0 running / 0 waiting requests.
- Original ODS GPU services restored healthy.
- Both GPUs returned to 0% utilization.

Raw telemetry and machine-readable results remain in:

`/home/michael/thermal-tests/runs/2026-07-29T20-38-12Z-no-gap-bottom600-top400-2m/`
