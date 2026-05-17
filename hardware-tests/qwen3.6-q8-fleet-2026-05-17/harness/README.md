# bench-fleet

Cross-platform reference benchmark for **Qwen3.6-27B-Q8** and **Qwen3.6-35B-A3B-Q8** across four AI hardware platforms. Goal: a debate-ending hardware comparison published in MMBT.

## The platforms

| Host       | Hardware                                  | Engine (canonical)              | Notes                                            |
|------------|-------------------------------------------|---------------------------------|--------------------------------------------------|
| Tower2     | RTX PRO 6000 Blackwell Workstation (96 GB VRAM, x86_64, 252 GB sys) | llama.cpp CUDA                  | Single-card canonical run on GPU 0 @ 600 W (matches 5090 TGP envelope); dual-card supplementary run separate |
| Strix Halo | AMD Ryzen AI MAX+ 395, x86_64, 124 GB UMA | llama.cpp **Vulkan** (canonical) | AMD APU. **ROCm 6.4.4 segfaulted in our environment** (see `../findings.md § Two backend-bug findings, Finding 1` and `AUDIT.md B4`); Vulkan is the working path and the row that appears in the cross-host ranking. A ROCm retry sub-study is queued. |
| Spark      | NVIDIA GB10 Grace Blackwell, aarch64, 121 GB UMA | llama.cpp CUDA-aarch64    | DGX Spark; aarch64                               |
| M5 MBP     | Apple M5 Max, arm64, 128 GB UMA           | llama.cpp Metal                 | New maxed MBP; passively cooled chassis          |

## Premise: identical bits, hardware-only difference

The single non-negotiable constraint:

> **Same model file (SHA-verified) and same llama.cpp source SHA on every host. The only variable is hardware.**

- vLLM, MLX, and other native-best engines do **not** run in the main study — they use their own quant formats, which would invalidate the comparison.
- A separate appendix study reports native-best numbers (vLLM on Tower2, MLX on M5) for context, never mixed into the hardware ranking.

## RTX 5090 read-across (Tower2 results)

Tower2 uses the **RTX PRO 6000 Blackwell Workstation Edition** — same Blackwell silicon as the consumer RTX 5090, but different SKU. For readers with a 5090:

**Tracks (within a few percent) on a 5090:**
- Decode tok/s and prefill tok/s at the same clocks
- Memory bandwidth (both GDDR7, same effective speed when bandwidth-bound)
- Power-vs-performance curve up to ~575 W (5090 TGP) — we run GPU 0 at 600 W cap, which sits 4 % above 5090 TGP
- Thermal behavior of the silicon (cooler design differs)

**Does NOT track on a 5090:**
- **VRAM ceiling: 32 GB on 5090 vs. 96 GB on PRO 6000.**
  - `Qwen3.6-27B-Q8_0` at 28.6 GB → barely fits a 5090, leaves <4 GB for KV cache. Q4 is the realistic 5090 quant.
  - `Qwen3.6-35B-A3B-Q8_0` at 36.9 GB → **does not fit a 5090.** A 5090 user needs Q4_K_XL (≈22 GB) for this model.
- ECC overhead (PRO 6000 has it, 5090 doesn't — small impact)
- Multi-instance GPU partitioning (PRO 6000 only)

**Bottom line:** if you have a 5090 and can fit the workload, you'll see numbers within a few percent of our PRO 6000 results. If the model doesn't fit, this study doesn't predict your numbers.

## Workload

### Main study — apples-to-apples grid

- **Models** (both at `Q8_0`, both `.gguf`, SHA-pinned):
  - `Qwen3.6-27B-Q8_0.gguf`
  - `Qwen3.6-35B-A3B-Q8_0.gguf`
- **Engine:** llama.cpp pinned to one SHA, compiled per-host with the appropriate backend.
- **Grid (per host, per model):**
  - Contexts: **1K, 4K, 16K, 32K**
  - Generation lengths: **128, 512, 2048 tokens**
  - Concurrencies: **1, 4, 8**
  - **N=10 per cell**, first 2 discarded as warmup
  - 4 × 3 × 3 × 10 = 360 inferences per (host, model). 4 hosts × 2 models × ~360 ≈ **2,880 inferences** for the main grid. Strix Halo was planned to run twice (ROCm and Vulkan); in practice ROCm 6.4.4 segfaulted and only Vulkan completed — see `../findings.md § Two backend-bug findings, Finding 1`. The ROCm retry is queued as a follow-up sub-study.

### Sustained-thermal sub-study

30-min continuous decode at each host's optimal-cell point, both models. Captures thermal throttle curves — critical for the M5 chassis and Strix Halo unified cooling debates.

### Bonus — Coder-Next on Blackwell

`Qwen3.6-Coder-Next-Q8_0` on Tower2 (and attempted on Spark; if the existing aarch64 garbage-tokens bug is unresolved, that's published as a finding). Separate report from the main study.

### Appendix — native-engine ceiling

- vLLM on Tower2 (CUDA, fp8/awq) — what discrete CUDA achieves with optimized software.
- MLX on M5 — what Apple Silicon achieves with optimized software.
- Labelled clearly as separate from the hardware comparison.

## Metrics

Captured per cell, every run, 1 Hz sampling, monotonic + wall-clock timestamped:

- **Throughput:** decode tok/s (headline), prefill tok/s, time-to-first-token
- **Power:** per-platform sampler (nvidia-smi / rocm-smi / tegrastats / powermetrics)
- **Thermals:** GPU/NPU/CPU temperatures over time (catches throttling)
- **Memory:** peak VRAM / unified-memory utilization
- **Engine + run metadata:** llama.cpp SHA, model SHA, backend, flags, kernel, OS, ambient room temp (manually entered), idle baseline temps

## Layout

```
bench-fleet/
├── README.md
├── run.sh                           # orchestrator
├── targets.json                     # hosts × engines × backends × model paths
├── lib/
│   ├── common.sh                    # SSH ControlMaster + host_exec helpers
│   ├── prepare-host.sh              # rsync model, build llama.cpp, preflight
│   ├── bench-host.sh                # run per-host grid
│   ├── sustained-host.sh            # 30-min sustained sub-study
│   ├── probe-power.sh               # 1 Hz cross-platform power sampler
│   ├── probe-thermals.sh            # 1 Hz cross-platform thermal sampler
│   ├── aggregate.sh                 # cross-host CSV pivot
│   ├── plot.sh                      # generate report plots
│   ├── report.sh                    # render REFERENCE.md
│   └── publish.sh                   # branch + PR to MMBT
├── engines/
│   ├── llama-cpp-cuda.sh            # Tower2
│   ├── llama-cpp-rocm.sh            # Strix Halo (broken in our env; see findings.md Finding 1)
│   ├── llama-cpp-vulkan.sh          # Strix Halo (canonical — the working path)
│   ├── llama-cpp-cuda-aarch64.sh    # Spark
│   ├── llama-cpp-metal.sh           # M5
│   ├── vllm.sh                      # appendix (Tower2)
│   └── mlx.sh                       # appendix (M5)
├── workloads/
│   ├── grid.json                    # context × gen-length × concurrency × N
│   └── prompts.jsonl                # MMBT-derived prompt corpus
└── results/
    └── <ts>/<host>/<engine>/...     # per-run JSON + CSV + samplers
```

## Status

Scaffolding in progress. See task list for current phase.
