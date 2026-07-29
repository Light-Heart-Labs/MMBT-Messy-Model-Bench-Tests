# Tower2 no-gap dual-GPU burn — 250 W / 250 W

- Run: `2026-07-29T22-36-43Z-no-gap-both250-10m`
- Physical configuration: GPU1/top directly above GPU0/bottom with no open-slot air gap
- Workload: one Qwen3.6-27B AWQ-INT4 vLLM engine per GPU
- Load: 32 concurrent chat-completion workers per GPU
- Warmup / measured / cooldown: 120 s / 600 s / 60 s
- Power caps: GPU0/bottom 250 W; GPU1/top 250 W
- Emergency cutoff: 96°C
- Result: **PASS**

## Measured results

| Metric | GPU0 / bottom | GPU1 / top |
|---|---:|---:|
| Mean board power | 249.994 W | 249.994 W |
| Mean utilization | 100% | 100% |
| Mean / P95 / maximum temperature | 51.85 / 52 / 54°C | 66.97 / 69 / 70°C |
| Mean graphics clock | 803.6 MHz | 775.5 MHz |
| First five-minute mean clock | 803.7 MHz | 779.0 MHz |
| Last five-minute mean clock | 803.2 MHz | 772.1 MHz |
| Mean / maximum fan speed | 30.7 / 31% | 40.1 / 42% |
| Hardware thermal slowdown | None | None |
| Software thermal slowdown | None | None |
| Hardware power brake | None | None |

Both GPUs held 250 W and 100% utilization for the full measured window. The top card averaged 15.12°C hotter and used 9.47 percentage points more fan, but its mean graphics clock was only 28.1 MHz (3.5%) below the bottom card. GPU1's first-to-last five-minute mean clock declined by 6.9 MHz (0.88%); GPU0 changed by -0.6 MHz.

The result demonstrates persistent positional thermal asymmetry even at low power, without a meaningful performance collapse or any NVIDIA thermal-limit event. Both cards were software-power-capped throughout, as expected.

## Request and host results

- Bottom GPU0: 608 completed requests, all HTTP 200; mean latency 33.43 s.
- Top GPU1: 512 completed requests, all HTTP 200; mean latency 37.50 s.
- CPU Tctl: 82.54°C mean, 84.2°C maximum.
- Maximum CCD temperature: 72.13°C mean, 83.5°C maximum.
- NVMe temperature: 42.9°C maximum.

## Cleanup verification

- Original 600 W power limits restored on both GPUs.
- Temporary GPU0 vLLM container removed.
- Original ODS GPU services restored.
- Both GPUs returned to 0% utilization before handoff.

Raw telemetry and machine-readable results remain in:

`/home/michael/thermal-tests/runs/2026-07-29T22-36-43Z-no-gap-both250-10m/`

