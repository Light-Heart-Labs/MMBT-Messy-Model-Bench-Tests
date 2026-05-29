# Findings — diagnosing Step-3.7-Flash NVFP4 on 2× sm_120 Workstation Blackwell

The diagnostic trail behind the four flags in [`README.md`](README.md), in the order the problems surfaced.

## Starting point

StepFun's reference NVFP4 command (from the model card / GitHub), trimmed to its essentials:

```bash
vllm serve stepfun-ai/Step-3.7-Flash-NVFP4 \
  --tensor-parallel-size 4 --enable-expert-parallel \
  --quantization modelopt --kv-cache-dtype fp8 \
  --reasoning-parser step3p5 --tool-call-parser step3p5 --trust-remote-code
```

It assumes a 4–8 GPU datacenter server. Adapting to TP=2 on 2× RTX PRO 6000 surfaced three independent failures plus one harness-integration detail.

## Problem 1 — TP hangs on the first multi-GPU collective

**Symptom.** With `--tensor-parallel-size 2`, the server hung. Across attempts it hung at different points — NCCL init, CUDA-graph capture, and (with `--enforce-eager`) FlashInfer attention warmup — but always the same signature: both GPUs pinned at **100 % utilisation but only ~130 W draw** (a busy-wait spin, not real compute), workers silent, `EngineCore` heartbeating `No available shared memory broadcast block found in 60 seconds`.

**Diagnosis.** `nvidia-smi topo -m` reports the two GPUs connected by `NODE` — PCIe through the host bridge, **no NVLink** (workstation Blackwell dropped NVLink):

```
        GPU0    GPU1    CPU Affinity    NUMA Affinity   GPU NUMA ID
GPU0     X      NODE    0-47            0               N/A
GPU1    NODE     X      0-47            0               N/A
```

(`NODE` = traversal of the PCIe host bridge within a single NUMA node; no `NV#` link.) The engine log showed `Using ['CUSTOM', 'PYNCCL'] all-reduce backends` with `disable_custom_all_reduce=False`. vLLM's CUSTOM all-reduce kernel requires GPU peer-to-peer; on a no-P2P PCIe pair the first real all-reduce deadlocks.

**Fix.** `--disable-custom-all-reduce` (force PYNCCL) + `-e NCCL_P2P_DISABLE=1`. After this the log reads `Using ['PYNCCL']` and the warmup forward pass completes. This single flag was the root cause of *all three* apparent hangs — the earlier "NCCL-init" and "cudagraph-capture" hangs were the same custom-all-reduce deadlock at different first-collective sites.

## Problem 2 — Marlin fallback instead of native FP4

**Symptom.** `WARNING marlin_utils_fp4.py: Your GPU does not have native support for FP4 computation but FP4 quantization is being used. Weight-only FP4 compression will be used leveraging the Marlin kernel.` — i.e. NVFP4 weights dequantised and run through Marlin, not native FP4 tensor cores.

**Diagnosis.** The warning is misleading on sm_120. Live probes inside the container:

```python
cutlass_scaled_mm_supports_fp4(120)      # True  — native cutlass FP4 GEMM is compiled
has_flashinfer_b12x_gemm()               # True
has_flashinfer_cutlass_fused_moe()       # True
has_flashinfer_trtllm_fused_moe()        # True
```

Native FP4 *is* available. The fallback came from the **MoE expert path**, whose backend defaults to `auto` → Marlin. The modern knob is `--moe-backend` (the old `VLLM_USE_FLASHINFER_MOE_FP4` env var is deprecated).

**First attempts failed on activation support.** `--moe-backend flashinfer_b12x` and `flashinfer_cutlass` both raised:

```
ValueError: NvFp4 MoE backend 'FLASHINFER_B12X' does not support the deployment
configuration since kernel does not support MoEActivation.SWIGLUSTEP activation.
```

Step-3.7 uses a `SWIGLUSTEP` (clamped/stepped SwiGLU) MoE activation. Grepping which expert kernels declare it:

```
experts/marlin_moe.py        -> MoEActivation.SWIGLUSTEP   ✓
experts/cutlass_moe.py:711   -> MoEActivation.SWIGLUSTEP   ✓  (CutlassExpertsFp4 — VLLM_CUTLASS)
experts/triton_moe.py        -> SWIGLUSTEP   (non-FP4 kernel — not an --moe-backend NVFP4 option)
experts/deep_gemm_moe.py     -> SWIGLUSTEP   (FP8 kernel — not an --moe-backend NVFP4 option)
```

Scope matters here: the `--moe-backend` selector for an NVFP4 model only chooses among the eight `NvFp4MoeBackend` values, each mapped to one experts class (verified in `oracle/nvfp4.py`): `FLASHINFER_TRTLLM→TrtLlmNvFp4Experts`, `FLASHINFER_CUTLASS→FlashInferExperts`, `FLASHINFER_CUTEDSL→FlashInferCuteDSLExperts`, `FLASHINFER_CUTEDSL_BATCHED→…`, `FLASHINFER_B12X→FlashInferB12xExperts`, `VLLM_CUTLASS→CutlassExpertsFp4`, `MARLIN→MarlinExperts`, `EMULATION→…`. `triton_moe`/`deep_gemm_moe` declare SWIGLUSTEP but back *other* dtypes (non-FP4 / FP8) and are never reached by NVFP4 backend selection. So among the NVFP4 options, the FlashInfer paths (`b12x`, `cutlass`, `trtllm`, `cutedsl`) do **not** support SWIGLUSTEP — only `VLLM_CUTLASS` (vLLM's own `cutlass_scaled_fp4_mm`, backed by `CutlassExpertsFp4`) and `MARLIN` do. Empirically, `flashinfer_b12x` and `flashinfer_cutlass` were launch-tested and both raised the SWIGLUSTEP error; `trtllm`/`cutedsl` are excluded by the same source path (not separately launch-tested).

**Fix.** `--moe-backend cutlass`. Log then reads `Using 'VLLM_CUTLASS' NvFp4 MoE backend`, no Marlin warning.

## Problem 3 — VLLM_CUTLASS rejects expert-parallel

**Symptom.** With `--moe-backend cutlass --enable-expert-parallel`:

```
ValueError: NvFp4 MoE backend 'VLLM_CUTLASS' does not support the deployment
configuration since kernel does not support parallel config ... ep_size=2, use_ep=True
```

**Fix.** Drop `--enable-expert-parallel`. The experts then shard via tensor-parallel (the model fits comfortably: 58.6 GiB weights/GPU; vLLM reported 26.0 GiB *available KV cache memory* per GPU after weights + activation/cudagraph reservation — note that's the measured KV figure, lower than a naive 88 GiB budget − 58.6 GiB weights, because activations and the cudagraph reserve consume the difference). StepFun's reference command includes EP because their datacenter path uses a FlashInfer backend that supports both EP and (on sm_100) presumably a different activation route; the VLLM_CUTLASS path we need on sm_120 does not.

## Problem 4 — harness max_tokens vs served max-model-len

**Symptom.** First smoke test failed instantly: `max_tokens=180000 cannot be greater than max_model_len=65536`.

**Diagnosis.** Not a model issue — the MMBT harness computes `max_tokens = min(180000, max_model_len − prompt − safety)` assuming the Qwen-family native `262144`. We had launched with `--max-model-len 65536`.

**Fix.** Serve at native `--max-model-len 262144`. KV-pool size is governed by free VRAM (2.06M tokens here), not context length, so the larger ceiling costs nothing for single-stream agentic runs. Re-ran smoke → PASS, 20/20 fields.

## Verification

- `Using 'VLLM_CUTLASS' NvFp4 MoE backend out of potential backends: [...]` — native FP4 on the experts.
- No `Weight-only FP4 compression` warning.
- All-reduce backend `['PYNCCL']` (not `['CUSTOM', 'PYNCCL']`).
- MMBT smoke (structured extraction, reasoning=medium): verdict PASS, field_accuracy 1.0 (20/20), clean `done_signal`.

## Resolved — CUDA Graphs work (no `--enforce-eager` needed)

The cudagraph-capture hang was Problem 1 in disguise. Relaunching **without** `--enforce-eager` (and with `--disable-custom-all-reduce` in place) captures cleanly — server ready in ~115 s — and is **4.7× faster single-stream** (TPOT 47 → 10 ms, ≈ 21 → 99 tok/s) and **1.8× higher batched output throughput** (530 → 963 output tok/s at conc=32) than eager. See [`throughput.md`](throughput.md). The recommended command runs with CUDA Graphs on; `--enforce-eager` is kept only as a fallback if a future image regresses capture.
