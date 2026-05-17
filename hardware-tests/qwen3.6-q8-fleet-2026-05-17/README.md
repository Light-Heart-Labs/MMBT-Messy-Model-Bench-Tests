# Cross-platform Q8 fleet benchmark — 2026-05-17

Same model file bytes, same llama.cpp source SHA, four different hardware platforms. The only variable is silicon (and the backend each platform requires).

- 4 hosts: NVIDIA Blackwell 6000 Tower (RTX PRO 6000, sm_120, CUDA), DGX Spark (GB10 Grace Blackwell, sm_121, CUDA aarch64), EVO X2 (AMD Ryzen AI MAX+ 395 / Strix Halo, Vulkan), M5 Max MacBook Pro 16" (Metal)
- 2 models, both `Q8_0` GGUF: Qwen3.6-27B (dense, 28.6 GB) and Qwen3.6-35B-A3B (MoE, 36.9 GB)
- Grid per (host, model): 4 ctx × 3 gen × 3 concurrency × N=10 (2 warmup discarded) = 360 inferences
- Engine pin: `llama.cpp` tag `b9151` SHA `67b2b7f2f2d6dac7962b219168a4c7a20c7359b7`, built per-host with its native backend
- Plus: vLLM appendix on the Blackwell 6000 Tower (FP8) for engine-comparison and to cover the model the llama.cpp/CUDA path crashes on (see `findings.md § Two backend-bug findings`)

In plain English: this bundle covers both **dense 27B** and **MoE 35B-A3B**
hardware behavior across the fleet. The Tower2 MoE native-Q8 llama.cpp row is
retracted because it crashes on Blackwell sm_120; the published Tower2 MoE row
is a clearly labeled vLLM FP8 exception defended in
`audit/SEMANTIC-EQUIVALENCE-35B-A3B.md`.

This is an early publication — the headline data is in, two companion sub-studies (full sustained-thermal tier, MMBT Phase B Q8 task-quality) are deferred. **Read `findings.md § Status of this PR` first** for the exact what-is-shipped-vs-deferred picture before reading any numbers.

## Read order

1. **`findings.md`** — full write-up. Status section, headline ranking, long-context behavior, held-multi-user analysis, sustained-thermal field measurements, cost-throughput at single-user peak, cross-host determinism, two backend-bug findings (ROCm on Strix, SOFT_MAX on Blackwell sm_120 MoE), hosts/methodology/reproducibility.
2. **`AUDIT.md`** — rigor self-audit. What's locked across hosts, what unavoidably varies, biases B1–B23, plug-meter calibration log, and the EVO X2 thermal-not-throttling within-cell trajectory.
3. **`NOTES-FOR-REVIEWERS.md`** — what feedback we want before round 2.
4. **`aggregate/`** — `canonical-headline.{csv,json}` (the cross-host ranking, the file to cite), `appendix-headline.{csv,json}` (Tower2 supplementary + engine-comparison rows, NOT part of the ranking), `cells.jsonl`, `all-inferences.jsonl`, `determinism.tsv`. See `aggregate/README.md` for the file selection guide. The unsplit `headline.{csv,json}` is kept for backwards compatibility but new readers should prefer the split.
5. **`audit/SEMANTIC-EQUIVALENCE-35B-A3B.md`** — quant-format audit defending the Tower2 vLLM FP8 row (Spark Q8 GGUF baseline vs Tower2 FP8 vLLM: first 251 chars identical, then synonymous phrasings; both are reasoning correctly about the same content).
6. **`workloads/prompts.jsonl`** + `.sha256` — the SHA-pinned natural-English prompt corpus that ran identically on every host.
7. **`sustained/`** — preliminary throttle-curve samples (one cell each on three of four hosts). The load-bearing sustained-thermal data for this PR is the psychrometer-anchored section in `findings.md`, not this subdirectory. Full sustained tier is a follow-up.
8. **`<host>/<model>/<backend>/<cell>/`** — per-cell raw: `cell.json` (summary), `batches.jsonl`, `inferences.jsonl` (per-request with content SHAs), `power.csv` + `thermals.csv` (1 Hz time series), `cell.meta.json`, `bench-cell.log`. llama-server debug logs are not included; they're regeneratable from the same SHA pins.

## Dense headline at a glance — single-user 27B Q8, conc=1

| host | backend | peak prefill tok/s | peak decode tok/s ± SD | decode @ ctx=16 K | TTFT @ ctx=16 K | silicon W (gpu-only) |
|---|---|---:|---:|---:|---:|---:|
| Blackwell 6000 Tower (single-RTX-6000 build) | cuda (llama.cpp) | 2230.8 | 49.78 ± 0.08 | 19.84 | 21.3 s | 500.4 |
| Blackwell 6000 Tower (vLLM FP8 appendix) | cuda-vllm | 6944.0 | 51.29 ± 0.00 | 49.32 | 2.3 s | — |
| M5 Max MacBook Pro | metal | 571.8 | 16.78 ± 0.19 | 16.10 | 30.8 s | 20.97 |
| DGX Spark | cuda-aarch64 | 750.6 | 7.60 ± 0.00 | 7.38 | 20.7 s | 41.74 |
| EVO X2 (Strix Halo) | vulkan | 292.3 | 7.82 ± 0.00 | 7.50 | 59.3 s | 114.4 |

## MoE headline at a glance — single-user 35B-A3B, conc=1

| host | backend | peak prefill tok/s | peak decode tok/s ± SD | decode @ ctx=16 K | TTFT @ ctx=16 K | note |
|---|---|---:|---:|---:|---:|---|
| Blackwell 6000 Tower | cuda-vllm | 37847.1 | 240.48 ± 0.04 | 227.97 | 0.4 s | FP8 vLLM exception; native Q8 llama.cpp row retracted |
| M5 Max MacBook Pro | metal | 2684.9 | 88.87 ± 0.12 | 80.28 | 7.8 s | Q8 GGUF |
| DGX Spark | cuda-aarch64 | 1738.4 | 54.90 ± 0.02 | 51.12 | 9.1 s | Q8 GGUF |
| EVO X2 (Strix Halo) | vulkan | 944.4 | 51.24 ± 0.26 | 20.42 | 123.7 s | Q8 GGUF, partial grid |

The MoE table is intentionally adjacent to the dense table so readers do not
mistake this bundle for a 27B-only study. For citation-grade details, use
`aggregate/canonical-headline.csv` plus the manifest status for each row.

Three things worth noting before you read the rest:

1. **Blackwell 6000 Tower wins prefill 3–8× across hosts**, single-user decode 3× over M5 Max and 6× over Spark / EVO X2 at short context. This is the discrete-GPU bandwidth-and-compute lead in its most natural place.
2. **At ctx=16 K under llama.cpp/CUDA, the Tower's decode collapses to 19.8 tok/s** — a llama.cpp + Blackwell kernel-size mismatch, not a silicon limit. Under vLLM/FP8 on the same GPU, ctx=16 K decode is **49.3 tok/s** (2.5× higher). The cross-host headline still favors the Tower, but understand which engine produced which number.
3. **Two of the four hosts' official vendor inference stacks were broken on this model** (ROCm 6.4.4 on Strix Halo, llama.cpp CUDA on Blackwell sm_120 for MoE). On a fresh out-of-box install of the official vendor path, two of these four platforms would have failed for the model the buyer most likely wanted. The cross-vendor paths (Vulkan, vLLM) delivered the working result. This is the second-most-important takeaway after the raw rankings.

## Reproducing

```bash
# 1. Fetch and verify the pinned model files
sha256sum --check <<'EOF'
f93f517f38e696d35a1a7df2c0e3155a64f4c4dcd662107a146ae263f7fb14ce  Qwen3.6-27B-Q8_0.gguf
d1a395809f65a43a13ad119eb4e7acdef1ac6d68120f39902c8ab96e72794a59  Qwen3.6-35B-A3B-Q8_0.gguf
EOF

# 2. Verify the prompt corpus
sha256sum --check workloads/prompts.jsonl.sha256

# 3. Build llama.cpp at the pinned SHA, per-host
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
git checkout 67b2b7f2f2d6dac7962b219168a4c7a20c7359b7
# CUDA host (sm_120 / sm_121): cmake -B build-cuda -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=<arch>-real
# Vulkan host: cmake -B build-vulkan -DGGML_VULKAN=ON
# Metal (M5):  cmake -B build-metal  -DGGML_METAL=ON
cmake --build build-<backend> -j

# 4. Per cell: load model once, run 10 batches of N=conc parallel requests
#    temperature=0 seed=42 cache_prompt=false stream=false
#    first 2 batches discarded as warmup
#    sample power + thermals at 1 Hz throughout
```

The harness used to drive all of this is vendored in `harness/`, with provenance
pinned in `harness/VENDORED-FROM-SHA.txt`. The upstream author repo is
`bench-fleet`; this bundle keeps the snapshot needed to reproduce the published
data.

## Where this fits in MMBT

- `../vllm-power-sweep-2026-04-29/` — Tower2-only LLM throughput vs GPU power cap. **Established 500 W ≈ 97% of optimal for vLLM Qwen3.6-27B serving** (memory-bandwidth-bound).
- `../ltx23-power-sweep-2026-05-05/` — Tower2-only LTX-2.3 video gen vs power cap. **Same hardware, different workload, different answer**: cap genuinely binds for diffusion (compute-bound).
- `../cpu-fullpower-2026-05-05/` — Tower2-only TR PRO 7965WX sustained-TDP validation (CPU side, 22 min stress-ng matrix).
- **This PR** — first cross-host hardware-comparison study on MMBT. Four platforms, single model bytes, single engine SHA. Companion vLLM/TensorRT-LLM/MLX multi-engine study and MMBT Phase B Q8 quality eval will follow.
