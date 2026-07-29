# Tower2 dual-GPU no-gap thermal study — 2026-07-29

Two RTX PRO 6000 Blackwell Workstation Edition GPUs were installed directly adjacent, with no open-slot air gap. GPU1 is the top card in `PCIEx16(G5)_1`; GPU0 is the bottom card in `PCIEx16(G5)_3`.

The initial cell holds the bottom GPU at 600 W and the top GPU at 400 W while each runs an independent Qwen3.6-27B AWQ-INT4 vLLM engine with 32 concurrent requests.

## Results

| Run | Bottom mean / max / fan | Top mean / max / fan | Throttling |
|---|---|---|---|
| [`bottom600-top400-2m`](bottom600-top400-2m/) | 76.25°C / 80°C / 45.4% mean | 76.58°C / 87°C / 45.2% mean | None |
| [`bottom600-top400-30m`](bottom600-top400-30m/) | 80.59°C / 84°C / 49.8% mean | 87.94°C / 92°C / 67.8% mean | None |

During the 30-minute run, the bottom card settled near 81°C at 50% fan while drawing 600 W. The top card settled near 88°C at 69–71% fan while drawing 400 W. The top card therefore ran about 7.4°C hotter and required roughly 18 percentage points more fan despite consuming 200 W less, but neither GPU recorded hardware thermal slowdown, software thermal slowdown, or hardware power-brake events.

This establishes that the adjacent-card layout is stable at a 600/400 W split. It does not isolate the effect of spacing because the existing air-gap reference used 600/600 W. Direction-reversed and equal-cap cells are needed to separate vertical position, neighbor heat, and airflow-channel effects.

## Read order

1. Each run directory's `REPORT.md` gives the human-readable result.
2. `summary.json` contains machine-readable aggregate statistics.
3. `gpu-telemetry.csv`, `host-telemetry.csv`, and `requests.csv` contain the raw samples.
4. `nvidia-before.txt`, `nvidia-after.txt`, events, payloads, and logs preserve the audit trail.
5. `dual-vllm-qwen27-30m.sh` and `summarize-dual-vllm.py` are the tested harness and summarizer.

The 30-minute run also recorded high host CPU thermals: 95.8°C maximum Tctl and a 98.6°C maximum CCD reading. Host CPU/CCD temperature, not GPU throttling, was the principal safety observation.
