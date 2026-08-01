# Tower2 dual-GPU Qwen3.6-27B 600 W burn — 30 minutes

- Run: `2026-07-29T19-35-57Z-qwen27-dual-600w-30m`
- Measured window: 2026-07-29 19:41:44–20:11:47 UTC
- Workload: one Qwen3.6-27B AWQ-INT4 vLLM instance per GPU
- Load: 32 concurrent chat-completion workers per GPU, 1,024 maximum output tokens
- Power limit: 600 W per GPU
- Warmup / measured / cooldown: 120 s / 1,800 s / 60 s
- Emergency GPU temperature cutoff: 96°C
- Result: **PASS**

## GPU results

| Metric | GPU0 | GPU1 |
|---|---:|---:|
| Mean board power | 599.987 W | 599.985 W |
| P95 board power | 600.09 W | 600.09 W |
| Samples at or above 570 W | 100% | 100% |
| Mean GPU utilization | 100% | 100% |
| Mean temperature | 85.14°C | 88.99°C |
| P95 temperature | 86°C | 89°C |
| Maximum temperature | 89°C | 92°C |
| Mean graphics clock | 2699.2 MHz | 2635.8 MHz |
| First 5m mean clock | 2708.3 MHz | 2646.5 MHz |
| Last 5m mean clock | 2695.0 MHz | 2631.1 MHz |
| First-to-last 5m clock change | -13.3 MHz (-0.49%) | -15.4 MHz (-0.58%) |
| Mean fan speed | 52.4% | 75.5% |
| Maximum fan speed | 53% | 79% |
| Hardware thermal slowdown | 0 samples / 0 µs | 0 samples / 0 µs |
| Software thermal slowdown | 0 samples / 0 µs | 0 samples / 0 µs |
| Hardware power-brake | 0 samples | 0 samples |

Both GPUs sustained the requested load for the complete measured window. GPU1 ran about 4°C hotter and approximately 63 MHz slower on average, with substantially higher fan demand, but it stabilized at 89°C for most of the run. Neither GPU accumulated thermal-slowdown time.

## Request results

- GPU0: 2,880 completed, all HTTP 200; mean latency 20.069 s.
- GPU1: 2,880 completed, all HTTP 200; mean latency 20.083 s.
- Total: 5,760 successful requests and no recorded request failures.
- Admitted requests drained in 8 seconds after the measured window.

## Host thermals

- CPU Tctl: 94.08°C mean, 95.5°C P95, 95.6°C maximum.
- Maximum CCD temperature: 90.72°C mean, 93.9°C P95, 96.6°C maximum.
- NVMe maximum temperature: 49.31°C mean, 51.9°C maximum.

The GPU result passed, but host CPU/CCD temperatures were high throughout the sustained workload and should be treated as the limiting thermal observation from this run.

## Cleanup verification

- Temporary GPU0 vLLM container removed.
- Sanctuary request queues returned to 0 running / 0 waiting.
- Original ODS GPU services restored and healthy.
- Both GPU power limits restored to their original 600 W setting.
- Both GPUs returned to 0% utilization after cleanup.

Raw telemetry, request logs, events, before/after NVIDIA state, container logs, and the machine-readable summary are stored in this run directory.
