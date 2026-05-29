# Running Step-3.7-Flash NVFP4 on 2× RTX PRO 6000 Blackwell (sm_120) — 2026-05-28

How to serve [`stepfun-ai/Step-3.7-Flash-NVFP4`](https://huggingface.co/stepfun-ai/Step-3.7-Flash-NVFP4) — a day-one (released 2026-05-28) 201B-parameter MoE vision-language model, ~11B active/token, 256k context — under vLLM on a **two-GPU workstation Blackwell** box, with the MoE experts running on **native NVFP4** kernels rather than the Marlin dequant fallback.

> **Personal research, not a recommendation.** This documents what it took to get *this specific model* serving correctly on *this specific rig* (Tower2: 2× RTX PRO 6000 Blackwell Workstation Edition, sm_120). StepFun's official docs only cover 4–8-GPU datacenter servers (TP=4–8) — there is no published 2× RTX PRO 6000 recipe anywhere (checked the model card, the StepFun GitHub, and the vLLM recipe page). This note fills that gap because the configuration was non-obvious and cost several hours to find. It is published as the setup companion to the Step-3.7-Flash microbench entry (results forthcoming).

## Headline — the working launch command

```bash
docker run -d --name vllm-step3p7 --gpus all --shm-size 16g \
  -e NCCL_P2P_DISABLE=1 \
  -v ~/models:/models:ro -p 127.0.0.1:8001:8000 \
  vllm/vllm-openai:stepfun37 \
  --model /models/stepfun-ai-Step-3.7-Flash-NVFP4 --served-model-name step3p7 \
  --host 0.0.0.0 --port 8000 \
  --tensor-parallel-size 2 --gpu-memory-utilization 0.92 \
  --trust-remote-code --quantization modelopt --kv-cache-dtype fp8 \
  --max-model-len 262144 \
  --moe-backend cutlass \
  --disable-custom-all-reduce \
  --reasoning-parser step3p5 --enable-auto-tool-choice --tool-call-parser step3p5
```

Verified: loads (58.6 GiB weights/GPU), KV cache 2.06M tokens (FP8, 7.88× concurrency at 262k ctx), CUDA Graphs capture cleanly (ready in ~115 s), serves, and passes the MMBT structured-extraction smoke test at **20/20 fields, accuracy 1.0**. Logs confirm `Using 'VLLM_CUTLASS' NvFp4 MoE backend` with **no Marlin warning** — i.e. the experts run on native FP4.

**Throughput** (cudagraph, FP8 KV, 600 W — full table in [`throughput.md`](throughput.md)): single-stream decode **≈ 99 tok/s** mean, scaling to **~1.5k tok/s mean aggregate output at 64-way concurrency**. Quick `vllm bench serve` readings, single run per cell — indicative, not a tuned sweep.

## The four non-obvious flags (and why each is required)

Everything below diverges from StepFun's reference command. See [`findings.md`](findings.md) for the full diagnostic trail.

1. **`--disable-custom-all-reduce` — the keystone.** Without it the server **hangs** on the first real tensor-parallel collective (manifesting variously at NCCL init, CUDA-graph capture, or FlashInfer attention warmup — all the same root cause). These are *Workstation* Blackwells with **no NVLink** (`nvidia-smi topo -m` reports `NODE` — PCIe through the host bridge), and vLLM's CUSTOM all-reduce kernel requires GPU peer-to-peer. Disabling it falls back to PYNCCL, which works. `-e NCCL_P2P_DISABLE=1` is set alongside for the same no-P2P reason.

2. **`--moe-backend cutlass` — for native FP4.** The default `auto` selects the **Marlin** weight-only-FP4 path (dequant-to-compute; vLLM warns "GPU does not have native support for FP4 computation"). That warning is misleading on sm_120: native FP4 *is* supported (`cutlass_scaled_mm_supports_fp4(120)=True`). The catch is the model's activation: Step-3.7 uses **`SWIGLUSTEP`** (a clamped/stepped SwiGLU), which the FlashInfer NVFP4 MoE kernels (`flashinfer_b12x`, `flashinfer_cutlass`, `flashinfer_trtllm`, `flashinfer_cutedsl`) **do not support** — among the eight NVFP4 `--moe-backend` options, only `VLLM_CUTLASS` (CLI `cutlass`) and `MARLIN` do. So `cutlass` is the *only* native-FP4 MoE backend compatible with this model.

3. **No `--enable-expert-parallel`.** StepFun's reference command includes it, but the `VLLM_CUTLASS` FP4 MoE kernel rejects expert-parallel (`ep_size=2`): the experts must be sharded by tensor-parallel instead. Including `--enable-expert-parallel` raises `does not support parallel config ... use_ep=True`.

4. **`--max-model-len 262144` (native), not a smaller value.** Unrelated to the model — this is an MMBT-harness detail: the harness computes its `max_tokens` budget assuming the Qwen-family native 262144 context. Serving at a smaller `--max-model-len` (e.g. 65536) produces `max_tokens=180000 > max_model_len` 400 errors. Serve at native 262144; the KV pool size is set by free VRAM, not context length, so it still fits (7.88× concurrency) and is irrelevant to single-stream agentic runs.

## Note — CUDA Graphs (the `--enforce-eager` caveat is resolved)

CUDA-graph capture was an early casualty of the same custom-all-reduce hang (#1), so an interim version of this config used `--enforce-eager`. **That is no longer needed:** with `--disable-custom-all-reduce` in place, capture completes cleanly (server ready ~115 s) and is 4.7× faster single-stream / 1.8× higher batched **output** throughput than eager. The recommended command above runs with CUDA Graphs on, and the [`throughput.md`](throughput.md) numbers are representative. Keep `--enforce-eager` only as a fallback if a future image regresses capture.

## Environment

| | |
|---|---|
| GPUs | 2× NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 96 GB each, **sm_120 / cc 12.0**, no NVLink (PCIe `NODE`) |
| Driver | 595.58.03 |
| Power | both GPUs at 600 W (uncapped) for the run |
| Image | `vllm/vllm-openai:stepfun37` (`sha256:17fae7886712…de8db3`), vLLM `v0.1.dev16944+ge9c8946e7` |
| Model | `stepfun-ai/Step-3.7-Flash-NVFP4` — `quant_algo=NVFP4`, `kv_cache_quant_algo=FP8`, 13 shards / 124.4 GB, `model_type=step3p7` |
| Quant on disk | NVFP4 weights + FP8 KV are baked into the checkpoint; vLLM flags `--quantization modelopt --kv-cache-dtype fp8` |

## Read order

1. **`findings.md`** — the full diagnostic trail: each hang, how it was diagnosed (`nvidia-smi topo`, live `cutlass_scaled_mm_supports_fp4`/`has_flashinfer_*` probes, the `select_nvfp4_moe_backend` oracle, the SWIGLUSTEP activation-support grep), and how the flag was found.
2. **`throughput.md`** — quick `vllm bench serve` tok/s readings (cudagraph vs eager, concurrency 1→64).

(The working command + the four flags are in the sections above.)

## Companion

- The Step-3.7-Flash microbench results entry (3 reasoning levels: low/medium/high) — *forthcoming*.
- `../cpu-fullpower-2026-05-05/`, `../vllm-power-sweep-2026-04-29/`, `../ltx23-power-sweep-2026-05-05/` — other Tower2 rig-characterisation runs on the same 2× RTX PRO 6000 hardware.
