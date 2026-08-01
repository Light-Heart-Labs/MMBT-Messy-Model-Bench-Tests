# Tower2 no-gap dual-GPU burn — bottom 600 W / top 400 W

- Run: `2026-07-29T20-48-03Z-no-gap-bottom600-top400-30m`
- Physical configuration: GPU1/top directly above GPU0/bottom with no open-slot air gap
- Workload: one Qwen3.6-27B AWQ-INT4 vLLM engine per GPU
- Load: 32 concurrent chat-completion workers per GPU
- Warmup / measured / cooldown: 120 s / 1,800 s / 60 s
- Power caps: GPU0/bottom 600 W; GPU1/top 400 W
- Emergency cutoff: 96°C
- Result: **PASS**

## Measured results

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 599.987 W | 399.992 W |
| Mean utilization | 99.99% | 100% |
| Mean temperature | 80.59°C | 87.94°C |
| P95 temperature | 81°C | 89°C |
| Maximum temperature | 84°C | 92°C |
| Mean graphics clock | 2726.7 MHz | 1343.8 MHz |
| First 5m mean clock | 2723.6 MHz | 1373.4 MHz |
| Last 5m mean clock | 2727.8 MHz | 1336.6 MHz |
| Mean fan speed | 49.8% | 67.8% |
| P95 fan speed | 50% | 71% |
| Maximum fan speed | 50% | 71% |
| Hardware thermal slowdown | None | None |
| Software thermal slowdown | None | None |
| Hardware power brake | None | None |

The no-gap layout remained stable for the full 30-minute window. The 600 W bottom card settled near 81°C at 50% fan. The 400 W top card settled near 88°C at 69–71% fan, approximately 7.4°C hotter on average despite consuming 200 W less. Its temperature did not continue rising after the early ramp.

Relative to the earlier air-gap dual-600 W run:

- Bottom GPU0 improved from 85.14°C mean / 52.4% mean fan to 80.59°C / 49.8%.
- Top GPU1 improved from 88.99°C mean / 75.5% mean fan at 600 W to 87.94°C / 67.8% at 400 W.

The comparison changes both spacing and top-card power, so it cannot isolate a spacing effect. It does show that the close-card layout is operationally stable at the tested 600/400 W split, with the thermal cost concentrated in top-card fan duty rather than GPU throttling.

## Request and host results

- Bottom GPU0: 2,880 completed requests, all HTTP 200; mean latency 20.04 s.
- Top GPU1: 2,400 completed requests, all HTTP 200; mean latency 23.86 s.
- CPU Tctl: 94.82°C mean, 95.8°C maximum.
- Maximum CCD temperature: 93.10°C mean, 98.6°C maximum.
- NVMe temperature: 52.9°C maximum.

The host CPU/CCD thermal reading remains the primary safety concern, not either GPU.

## Cleanup verification

- Original 600 W power limits restored on both GPUs.
- Temporary GPU0 vLLM container removed.
- Sanctuary returned to 0 running / 0 waiting requests.
- Original ODS GPU services restored healthy.
- Both GPUs returned to 0% utilization.

Raw telemetry and machine-readable results remain in:

`/home/michael/thermal-tests/runs/2026-07-29T20-48-03Z-no-gap-bottom600-top400-30m/`
