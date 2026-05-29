# Step-3.7-Flash NVFP4 throughput on 2× RTX PRO 6000 Blackwell — quick readings

A short `vllm bench serve` battery to put real tokens/sec numbers on this rig. **Not** an exhaustive sweep — a ~25-minute set of readings to characterise the serving config in [`README.md`](README.md) before the microbench runs. Single rig, single run per cell; treat as indicative, not tight.

## Setup

- Model / config: exactly the [`README.md`](README.md) launch command — `stepfun-ai/Step-3.7-Flash-NVFP4`, **native NVFP4** (`--moe-backend cutlass`) + **FP8 KV**, TP=2, `--max-model-len 262144`, `--disable-custom-all-reduce`.
- Tool: `vllm bench serve --backend openai-chat --dataset-name random --ignore-eos` (in-container, hitting the live endpoint). `--ignore-eos` forces generation to the full output length so decode tok/s is measured cleanly.
- Hardware: 2× RTX PRO 6000 Blackwell (sm_120), **600 W** (uncapped), driver 595.58.03, vLLM `v0.1.dev16944` (`vllm/vllm-openai:stepfun37`).

## Headline — cudagraph (CUDA Graphs on, the representative config)

input len 1024, `--ignore-eos`:

| concurrency | output len | aggregate output tok/s | TPOT (mean) | TTFT (mean) | total tok/s (in+out) |
|---|---|---|---|---|---|
| 1  | 1024 | ~98   | 10.1 ms (≈99 tok/s/stream) | 171 ms | 196 |
| 8  | 512  | 475   | 16.7 ms | 80 ms | 1,434 |
| 32 | 256  | ~963  | 28.4 ms | 1,246 ms | 4,861 |
| 64 | 256  | 1,526 † | 36.0 ms | 1,503 ms | 7,694 |

Primary metric is **aggregate output tok/s** (generated tokens only); the last column is the in+out composite for reference, not the headline (this repo retracted leading with in+out totals — see `claims.yaml` `hw.q8.total-tokps-composite`). † conc=64 also reported a peak *instantaneous* output rate of 2,106 tok/s within the run (vLLM bench's "Peak output token throughput"); the 1,526 is the run mean.

**Single-stream decode ≈ 99 tok/s** (mean); aggregate output scales to **~1.5k tok/s mean at 64-way concurrency**. For a 201B-parameter MoE (~11B active/token) at 4-bit on two PCIe-connected workstation GPUs, that is a usable single-stream rate for interactive agentic use and reasonable batched throughput. TTFT jumps from ~80 ms (conc≤8) to ~1.2–1.5 s at conc≥32 — expected prefill queueing as concurrent requests contend, not a regression.

## CUDA Graphs vs eager (why `--enforce-eager` was dropped)

Same two cells, eager mode (`--enforce-eager`) vs cudagraph:

| cell | eager | cudagraph | speedup |
|---|---|---|---|
| conc=1 single-stream (TPOT) | 47.3 ms (~21 tok/s) | 10.1 ms (~99 tok/s) | **4.7×** |
| conc=32 aggregate **output** tok/s | 530 | 963 | **1.8×** |

(Speedup on output tokens, not the in+out composite. The in+out total also moves 2,674 → 4,861, the same ~1.8×.)

CUDA-graph capture initially appeared to hang — but that was the same custom-all-reduce deadlock documented in [`findings.md`](findings.md) (Problem 1). With `--disable-custom-all-reduce` in place, **capture completes cleanly** (server ready in ~115 s) and delivers the speedups above. The earlier `--enforce-eager` workaround is therefore **no longer needed**; the recommended config runs with CUDA Graphs on, and the throughput numbers above are representative (not eager-throttled).

## Caveats

- Single run per cell, `random` dataset, `--ignore-eos` — these measure raw serving throughput, not task-shaped workloads. The microbench (agentic, variable-length, reasoning on) will see different effective rates.
- Native FP4 confirmed (`Using 'VLLM_CUTLASS' NvFp4 MoE backend`, no Marlin warning) — see [`findings.md`](findings.md).
- Numbers are for this exact image/version; FP4 kernel performance on sm_120 is young and likely to move with vLLM releases.
