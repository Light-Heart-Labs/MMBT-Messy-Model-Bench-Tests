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

**Diagnosis.** `nvidia-smi topo -m` reports the two GPUs connected by `NODE` — PCIe through the host bridge, **no NVLink** (workstation Blackwell dropped NVLink). The engine log showed `Using ['CUSTOM', 'PYNCCL'] all-reduce backends` with `disable_custom_all_reduce=False`. vLLM's CUSTOM all-reduce kernel requires GPU peer-to-peer; on a no-P2P PCIe pair the first real all-reduce deadlocks.

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
experts/triton_moe.py        -> SWIGLUSTEP
experts/deep_gemm_moe.py     -> SWIGLUSTEP
```

The FlashInfer fused-MoE paths (`flashinfer_b12x`, `flashinfer_cutlass`, `flashinfer_trtllm`, `flashinfer_cutedsl`) do **not** support SWIGLUSTEP. Of the native-FP4 options, only `VLLM_CUTLASS` (vLLM's own `cutlass_scaled_fp4_mm`, which `CutlassExpertsFp4` backs) supports it.

**Fix.** `--moe-backend cutlass`. Log then reads `Using 'VLLM_CUTLASS' NvFp4 MoE backend`, no Marlin warning.

## Problem 3 — VLLM_CUTLASS rejects expert-parallel

**Symptom.** With `--moe-backend cutlass --enable-expert-parallel`:

```
ValueError: NvFp4 MoE backend 'VLLM_CUTLASS' does not support the deployment
configuration since kernel does not support parallel config ... ep_size=2, use_ep=True
```

**Fix.** Drop `--enable-expert-parallel`. The experts then shard via tensor-parallel (the model fits comfortably: 58.6 GiB weights/GPU, 26 GiB free for KV). StepFun's reference command includes EP because their datacenter path uses a FlashInfer backend that supports both EP and (on sm_100) presumably a different activation route; the VLLM_CUTLASS path we need on sm_120 does not.

## Problem 4 — harness max_tokens vs served max-model-len

**Symptom.** First smoke test failed instantly: `max_tokens=180000 cannot be greater than max_model_len=65536`.

**Diagnosis.** Not a model issue — the MMBT harness computes `max_tokens = min(180000, max_model_len − prompt − safety)` assuming the Qwen-family native `262144`. We had launched with `--max-model-len 65536`.

**Fix.** Serve at native `--max-model-len 262144`. KV-pool size is governed by free VRAM (2.06M tokens here), not context length, so the larger ceiling costs nothing for single-stream agentic runs. Re-ran smoke → PASS, 20/20 fields.

## Verification

- `Using 'VLLM_CUTLASS' NvFp4 MoE backend out of potential backends: [...]` — native FP4 on the experts.
- No `Weight-only FP4 compression` warning.
- All-reduce backend `['PYNCCL']` (not `['CUSTOM', 'PYNCCL']`).
- MMBT smoke (structured extraction, reasoning=medium): verdict PASS, field_accuracy 1.0 (20/20), clean `done_signal`.

## Open question / next experiment

`--enforce-eager` is still set (see README caveat). The cudagraph-capture hang was Problem 1 in disguise; with `--disable-custom-all-reduce` now in place, capture may succeed. Untested. Until a cudagraph run is confirmed, treat throughput/latency from this config as eager-mode (a floor, not the native-FP4 ceiling). This is why the companion microbench entry reports its throughput numbers as eager-qualified.
