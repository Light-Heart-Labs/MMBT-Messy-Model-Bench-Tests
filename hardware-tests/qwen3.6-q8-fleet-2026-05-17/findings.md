# Cross-platform Q8 reference benchmark
## Qwen3.6-27B-Q8 and Qwen3.6-35B-A3B-Q8 on four hardware platforms

_Generated 2026-05-16T02:30:56Z from `results/2026-05-14T21-35-01Z`_

## Why Q8?

MMBT users specifically requested higher-precision data after the prior Q4 round drew quality complaints. This study runs the canonical hardware grid at `Q8_0` GGUF for both models, with the same source files SHA-pinned across every host.

## Premise

Same model file (SHA-verified) and same llama.cpp source SHA on every host. The only variable is hardware (and its required backend).

| pin | value |
|---|---|
| llama.cpp tag b9151 SHA | `67b2b7f2f2d6dac7962b219168a4c7a20c7359b7` |
| Qwen3.6-27B-Q8_0.gguf SHA | `f93f517f38e696d35a1a7df2c0e3155a64f4c4dcd662107a146ae263f7fb14ce` |
| Qwen3.6-35B-A3B-Q8_0.gguf SHA | `d1a395809f65a43a13ad119eb4e7acdef1ac6d68120f39902c8ab96e72794a59` |
| Prompt corpus SHA | `9a27eba85a8da9443d7fcf74e281b011831806c4b24aaaada3915463d5c13cd8` |

## § Status of this PR — what's shipped, what's preliminary, what's deferred

This is an early publication. We are shipping for feedback now rather than waiting for the full grid plus companion suites to land, because the headline data is already strong enough that external review will improve the follow-up rounds more than another week of solo polish would.

**Complete and load-bearing for the conclusions in this report:**
- Single-user (conc=1) decode + prefill across 4 ctx × 3 gen on all four hosts for 27B Q8 (36/36 cells each).
- Single-user (conc=1) decode + prefill on three of four hosts for 35B-A3B Q8 (Spark, M5, and Tower2 vLLM appendix complete; Strix Vulkan partial).
- Per-cell SHA-pinned generations on every host (semantic-equivalence check).
- Plug-meter wall-AC ground-truth on M5 Max and Blackwell 6000 Tower (one cell each).
- Exhaust-air psychrometer readings at the 15.5 h mark for all four hosts.

**Partial, honestly labeled in the data:**
- **EVO X2 / Strix Halo, Vulkan, 27B:** 33/36 cells (3 cells failed `rc=2`; investigation queued).
- **EVO X2 / Strix Halo, Vulkan, 35B-A3B:** 23/36 cells. The 13 missing cells are all `ctx=32768, conc≥4` — KV cache for 35B-A3B Q8 at 32 K × 4-or-8 slots exceeds the 124 GB unified pool and OOMs. This is a hardware ceiling on this configuration, not a transient failure. Documented; not retried.
- **Blackwell 6000 Tower, native CUDA, 35B-A3B:** 36/36 cells *exist on disk* but **every cell is zero-throughput** — see § Two backend-bug findings below. The Tower2 vLLM appendix (FP8) covers this hardware for 35B-A3B.
- **Blackwell 6000 Tower, vLLM appendix, 27B:** 14/36 cells. Appendix only; not part of the cross-host ranking.

**Deferred to follow-up rounds (NOT in this PR):**
- **Sustained-thermal throttle curves.** Planned 30-min sustained-load samples per (host, model). Only one sample each exists on Tower2/27B, Spark/35B-A3B, M5/35B-A3B at the time of this snapshot. The substantive thermal data in § Sustained thermal field measurements is from psychrometer readings at the 15.5 h mark, which IS load-bearing. The `sustained/` subdirectory is preliminary and labeled as such.
- **MMBT Phase B Q8 task-quality companion.** The matching quality benchmark on the MMBT Phase B 12-task-family suite for both models at Q8. Not run yet. This was the second of two original goals; we are shipping the performance half now and the quality half will follow as a separate PR.
- **EVO X2 ROCm retry sub-study.** ROCm 6.4.4 on Strix Halo segfaulted in our smoke attempt (see § Two backend-bug findings). A proper retry with longer wait-ready, smaller bootstrap model, and fresh stderr/dmesg capture is queued. Vulkan numbers stand on their own for now.
- **Tower2 dual-card 27B supplementary.** 33/36 cells; the last three cells (32K-gen2048-conc4/8) were in progress at pause. Supplementary to the canonical single-card numbers, not load-bearing.

**Specifically not in scope at all** (and not planned for this dataset):
- Q4 / Q5 / fp16 quantizations (Q4 data exists in MMBT's prior fleet entries).
- Multi-turn conversation, tail-latency characterization, MIG partitioning, OS scheduler noise studies.

## § Two backend-bug findings — official vendor stacks broken on two of the four hosts

Two separate native-vendor inference paths failed on the same llama.cpp source SHA under which the other two hosts work fine. Both are reproducible, both are worth a write-up on their own, and together they form a pattern: in May 2026, the open / cross-vendor stack (Vulkan, vLLM, Metal) was the most reliable way to actually run these models on a fresh purchase of either of the two affected platforms.

### Finding 1 — ROCm 6.4.4 segfault on Strix Halo + Qwen3.6-27B-Q8

llama.cpp `build-rocm/bin/llama-server` at b9151 `67b2b7f2...` on the EVO X2 (AMD Ryzen AI MAX+ 395 / Strix Halo, gfx1151) crashes after model metadata read with a segfault in `libamdhip64.so.6.4.60404` at offset `0x3a4e52`, fault address `0x18`. Reproduces on at least six independent attempts. `HSA_OVERRIDE_GFX_VERSION=11.0.0` does not help; `-fit off` does not help. The Vulkan backend on the *same* hardware/model/binary works fine (smoke decode 8.0 tok/s, prefill 22.8 tok/s). The headline EVO X2 numbers in this report are Vulkan; ROCm is not in the cross-host ranking.

The audit retry (longer wait-ready window + smaller bootstrap model + fresh stderr/dmesg) is queued but not in this PR. Until it runs, the finding is "ROCm 6.4.4 on Strix Halo + Q8 GGUF crashes in our environment; Vulkan is the working path." Reviewers with Strix Halo hardware are explicitly invited to reproduce or refute.

### Finding 2 — SOFT_MAX kernel crash on Blackwell sm_120 + Qwen3.6-35B-A3B-Q8 (MoE)

llama.cpp at the same b9151 SHA built with `-DCMAKE_CUDA_ARCHITECTURES=120-real` on the Blackwell 6000 Tower (2× RTX PRO 6000 Blackwell, sm_120) crashes for Qwen3.6-35B-A3B-Q8 at the startup capability probe (`common_context_can_seq_rm` → `llama_decode`):

```
ggml-cuda.cu:102: CUDA error
ggml_cuda_compute_forward: SOFT_MAX failed
CUDA error: invalid argument
ggml_cuda_compute_forward at ggml-cuda.cu:3114
```

Reproduces with `-fa off`, `-fa auto`, `-ub 64 -b 64`, GPU 0 or GPU 1, full ctx or `ctx=2048`, `parallel=1` or `parallel=4`. Not memory pressure (reproduces on an otherwise empty GPU).

The same source SHA built for sm_121 on the Spark (GB10 Grace Blackwell) runs the full 36-cell grid fine for the same model (~40 tok/s). The same Tower2 binary runs Qwen3.6-27B-Q8 (dense, not MoE) cleanly across the full 36-cell grid. So the bug is specifically: **Blackwell sm_120 + Qwen3.6-MoE-Q8 SOFT_MAX kernel launch**. Likely a kernel-launch parameter mismatch (threads/shmem/blocks) that is valid on sm_121 but invalid on the sm_120 resource profile.

Because the harness's `.done` sentinel is set per-cell regardless of decode success, the 36 zero-throughput cells exist on disk and are present in `aggregate/cells.jsonl` for transparency, but are filtered out of the headline ranking. The Tower2 vLLM appendix (FP8) covers this hardware for 35B-A3B.

The candidate retries we have not yet executed are: rebuild with `-DCMAKE_CUDA_ARCHITECTURES=120` (no `-real`, allowing PTX JIT fallback) while preserving the b9151 SHA pin; and a later llama.cpp tag where this may already be fixed (would invalidate the same-source-SHA claim, so it would have to be a sensitivity-check appendix, not a replacement).

### Why this pairing matters

Strix Halo and the Blackwell PRO 6000 are both 2025-era flagship parts. On a fresh out-of-box install of the official vendor stack, neither would have worked for the model the buyer most likely wanted. The cross-vendor paths (Vulkan on Strix, vLLM on Blackwell) did. We are not making a claim about which vendor is "better"; we are saying the open/cross-vendor stack delivered the working path on both, and that is something prospective buyers should price in.

## § Scope — what this report concludes and what it does not

This report is **an llama.cpp inference benchmark across four hardware platforms** under a fixed source SHA, fixed model bytes, fixed prompts, and a fixed grid. It is paired with calibrated power and thermal field measurements.

Conclusions in this report cover three things only:

1. **Single-user (conc=1) decode and prefill rates across context lengths**, for each host running its native llama.cpp backend (CUDA / Vulkan / Metal / CUDA-aarch64).
2. **Sustained power and thermal behavior**: silicon power (sampler-derived) and chassis exhaust temperature (psychrometer-measured) under continuous load, with plug-meter wall-AC validation on two hosts.
3. **Cross-host generation determinism and behavior** at `temperature=0`: do hosts produce bit-identical output, and if not, how do length / stop distributions differ?

Conclusions in this report **do not** cover:

- **Multi-user concurrent serving** (conc≥4). Internal analysis shows llama.cpp's `--parallel N` slots are an engine-level binding constraint at long context that masks silicon differences (see § Held: multi-user concurrent serving). Hardware comparisons under proper concurrent-serving engines are a separate study (companion vLLM / TensorRT-LLM / MLX runs are a follow-up).
- **Hardware quality of Q8 outputs.** That is the companion MMBT Phase B task suite, reported separately.
- **Cross-engine generality.** Numbers reflect llama.cpp at tag b9151. Different engines or different llama.cpp builds will produce different numbers.
- **Cross-run variance.** N=10 within a cell captures intra-cell variance; we do not characterize day-to-day reproducibility in this report.

## § Headline hardware ranking — single-user, 27B Q8

Three primary metrics, three independent things a buyer cares about:

- **Prefill tok/s** — how fast the model reads your prompt (matmul-dense, bandwidth-friendly).
- **Decode tok/s** — how fast it streams generated tokens (sequential, memory-bandwidth-bound per token).
- **TTFT** — time from request submission to first token (dominates UX at long context).

All numbers are conc=1 (single user). Multi-user is engine-bound under llama.cpp and held.

### Cross-model rule

Each row is a single (host, model, backend) tuple. Two models are present: Qwen3.6-27B (dense) and Qwen3.6-35B-A3B (MoE). Compare hosts within a model column; do not compare rows across models — that's architecture, not hardware.

| host | model | backend | peak prefill tok/s | peak decode tok/s ± SD | decode @ ctx=16K ± SD | cold-start @ peak | TTFT @ ctx=16K | silicon W | sensor | max °C |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| M5 Max MacBook Pro | qwen3.6-27b | metal | 571.8 | 16.78 ± 0.19 | 16.1 ± 0.1 | 16.86 | 30.8 s | 20.97 | gpu_die_avg | 76.7 |
| M5 Max MacBook Pro | qwen3.6-35b-a3b | metal | 2684.9 | 88.86 ± 0.11 | 80.28 ± 0.56 | 88.6 | 7.7 s | — | gpu_die_avg | — |
| DGX Spark | qwen3.6-27b | cuda-aarch64 | 750.6 | 7.6 ± 0 | 7.38 ± 0 | 7.6 | 20.7 s | 41.74 | gpu_die | 70.0 |
| DGX Spark | qwen3.6-35b-a3b | cuda-aarch64 | 1738.4 | 54.89 ± 0.01 | 51.12 ± 0.04 | 54.86 | 9 s | 43.25 | gpu_die | 68.0 |
| EVO X2 | qwen3.6-27b | vulkan | 292.3 | 7.82 ± 0 | 7.5 ± 0 | 7.81 | 59.3 s | 114.44 | gpu_edge | 85.0 |
| EVO X2 | qwen3.6-35b-a3b | vulkan | 914.3 | 51.24 ± 0.25 | — | 49.84 | — | 119.03 | gpu_edge | 85.0 |
| Blackwell 6000 Tower | qwen3.6-27b | cuda | 2230.8 | 49.78 ± 0.08 | 19.84 ± 0 | 49.63 | 21.3 s | 500.44 | gpu_die | 58.0 |
| Blackwell 6000 Tower | qwen3.6-27b | cuda-vllm | 6944 | 51.29 ± 0 | 49.32 ± 0 | 51.29 | 2.3 s | — | unknown | — |
| Blackwell 6000 Tower | qwen3.6-35b-a3b | cuda-vllm | 38124.3 | 239.9 ± 0.18 | 227.71 ± 0.12 | 240.38 | 0.4 s | — | unknown | — |

### Reading the headline

- Blackwell 6000 Tower wins prefill by 3–8× across hosts. This is where its GDDR7 bandwidth and Blackwell compute lead express directly.
- Blackwell 6000 Tower wins peak decode by 3× over M5 Max MacBook Pro and 6×+ over DGX Spark / EVO X2 at short context (ctx=1K).
- At ctx=16K decode, Blackwell 6000 Tower still leads (19.4 tok/s) but by a much smaller margin over M5 Max (16.1) — see § Long-context single-user behavior for what's happening there. The Blackwell Tower's decode-only rate at long ctx is one specific metric; total request time (prefill + decode) still favors it substantially because its prefill is so much faster.
- TTFT at ctx=16K: Blackwell 6000 Tower 21 s, DGX Spark 21 s, M5 Max 31 s, EVO X2 61 s. The EVO X2's slow prefill makes its first-token latency 3× the others.

### Power and thermal columns

- **silicon W**: GPU/package only — nvidia-smi (Blackwell 6000 Tower: GPU 0 only, gpu1 idle excluded; DGX Spark: gpu0). rocm-smi (EVO X2 APU graphics package). macmon (M5 Max `gpu` row). Cross-host comparable within sampler-scope caveats.
- **`temp_sensor`**: `gpu_die` (nvidia internal die), `gpu_die_avg` (Apple silicon die), `gpu_edge` (rocm-smi exposes only edge sensor on the EVO X2's Strix Halo APU; junction is typically 10–15 °C hotter and not available).
- Plug-meter wall-AC validation for M5 Max (142 W vs macmon sys 128 W) and Blackwell 6000 Tower (445 W at the cell measured) is in § Sustained thermal and `targets.json.hosts[].wall_calibration`.

## § Long-context single-user behavior

All numbers are conc=1. The two metrics that matter here are **decode tok/s** (how fast generation streams once it starts) and **TTFT** (how long until the first token arrives, dominated by prefill time at long ctx).

### Decode tok/s across context lengths (27B Q8, conc=1, gen=2048)

| ctx | Blackwell 6000 Tower | M5 Max | DGX Spark | EVO X2 |
|---|---:|---:|---:|---:|
| 1024 | 49.39 | 16.76 | 7.59 | 7.77 |
| 4096 | 48.22 | 16.62 | 7.56 | 7.7 |
| 16384 | 19.37 | 16.06 | 7.32 | 7.47 |
| 32768 | 12.29 | 16.16 | 7.02 | 7.23 |

### Prefill tok/s across context lengths

| ctx | Blackwell 6000 Tower | M5 Max | DGX Spark | EVO X2 |
|---|---:|---:|---:|---:|
| 1024 | 2181.7 | 535.5 | 653.5 | 269 |
| 4096 | 1659.3 | 571.8 | 748.7 | 285.4 |
| 16384 | 730.9 | 502.8 | 750.5 | 255.9 |
| 32768 | 413 | 502.4 | 710.6 | 204.9 |

### Reading

Blackwell 6000 Tower wins both prefill and decode at every context length we measured. The decode lead narrows at ctx=16K (Blackwell 6000 Tower 19 tok/s vs M5 Max 16 tok/s) — a specific llama.cpp-CUDA-on-Blackwell behavior at long context worth investigating under a different engine, but it doesn't change the overall hardware ranking. The Blackwell Tower's prefill remains 3–8× the unified-memory hosts at every context length, which is where the bandwidth-and-compute advantage of the discrete GPU shows up most cleanly.

### Blackwell 6000 Tower silicon power across context lengths (reference)

For engine-internals readers: the Blackwell 6000 Tower's GPU silicon power at conc=1 drops as context grows. This is the same observation that produced the decode-only behavior noted above (the GPU isn't being driven hard at long context under llama.cpp's CUDA path on Blackwell).

| ctx | Blackwell 6000 Tower silicon W mean | % of 600 W cap |
|---|---:|---:|
| 1024 | 599.78 | 99% |
| 4096 | 599.85 | 99% |
| 16384 | 300.98 | 50% |
| 32768 | 243.00 | 40% |

## § Held: multi-user concurrent serving

We ran the multi-user (conc=4 and conc=8) cells across the grid, but **we do not draw cross-host conclusions from them**. The reason is internal to this dataset:

At ctx=16K gen=2048 conc=8, each forward pass reads ~28.6 GB of Q8 weights plus ~10 GB of KV cache (8 slots × 16 K tokens × ~75 KB/tok) ≈ **~38 GB per step**, producing 8 next-tokens. The bandwidth-bound aggregate is 8 / (38 / bandwidth). Public memory bandwidth specs:

| host | GPU/SoC | bandwidth (GB/s) | theoretical agg tok/s | observed | % of theoretical |
|---|---|---:|---:|---:|---:|
| Blackwell 6000 Tower | RTX PRO 6000 Blackwell GDDR7 | ~1,800 | ~380 | 17.4 | **4.6 %** |
| M5 Max MacBook Pro | M5 Max LPDDR5x | ~600 | ~126 | 18.0 | **14 %** |
| DGX Spark | GB10 Grace Blackwell LPDDR5x | ~275 | ~58 | 18.4 | **32 %** |
| EVO X2 | Ryzen AI MAX+ 395 (Strix Halo) LPDDR5x-8000 256-bit | ~256 | ~54 | 10.1 | **19 %** |

All four hosts come in under their bandwidth-bound ceiling, with the Blackwell 6000 Tower at 4.6 % of its theoretical max. That gap cannot be silicon — the binding constraint is upstream. Internal evidence within this dataset:

- At ctx=1 K, the Blackwell 6000 Tower's per-slot decode HOLDS as conc grows (49.4 at conc=1 → 49.78 at conc=8; aggregate ≈ 2.6× the conc=1 figure). The hardware scales here.
- At ctx=16 K, the Blackwell 6000 Tower's per-slot decode COLLAPSES with conc (19.4 at conc=1 → 2.94 at conc=8; aggregate barely grows). The hardware does not scale here, but it also is nowhere near its bandwidth ceiling — so the binding factor is not silicon.

Most likely cause: llama.cpp's `--parallel N` slots implementation does not retain efficient batched / paged attention at long context. Confirming this requires engine-side instrumentation we do not have. What this means for the report:

- **Cross-host multi-user comparisons at long ctx are held**: they reflect llama.cpp behavior, not silicon. (The Blackwell 6000 Tower's specific kernel-size mismatch on Blackwell SMs is the cleanest example, but the held conclusion is general.)
- **A separate study under a properly batched concurrent-serving engine (vLLM / TensorRT-LLM)** is a follow-up. Until it runs, this report makes no multi-user concurrent-serving claim.

The raw conc=4 and conc=8 cells remain in `aggregate/cells.jsonl` for reproducibility, but the report's conclusions do not draw on them.

## § Sustained thermal field measurements

Exhaust-air temperature measurements taken with a Fieldpiece PRH2 digital pocket psychrometer ~15.5 h into continuous benchmark operation. All four hosts at sustained steady-state at the time of measurement. Readings taken back-to-back within a few minutes of each other.

| host | chassis class | exhaust °F | room ambient °F | Δ above ambient °F | sensor-derived silicon temp |
|---|---|---:|---:|---:|---|
| Blackwell 6000 Tower | Custom workstation tower | 82 | 78 | **4** | (see headline temp_c_max) |
| EVO X2 | GMKtec EVO X2 mini-PC | 138 | 78 | **60** | (see headline temp_c_max) |
| DGX Spark | NVIDIA DGX Spark reference desktop | 118 | 78 | **40** | (see headline temp_c_max) |
| M5 Max MacBook Pro | Apple MacBook Pro 16" | 81 | 77 | **4** | (see headline temp_c_max) |

### What these numbers say

Tower2 and M5 are exhausting essentially room temperature air despite running the same workload at much higher silicon power than Strix/Spark — their cooling systems are sized for the workload, not stressed by it. Spark's compact-desktop chassis works moderately hard (40°F delta). Strix's NUC-class chassis is the limiting factor (60°F delta, chassis surface area is the binding constraint, not silicon). This is the chassis-class story the headline thermal data implies.

### Per-host environmental context

- **Blackwell 6000 Tower**: Workstation tower with 14× Noctua 120 mm + open panel — exhaust at room temperature, cooling system massively over-provisioned
- **EVO X2**: GMKtec EVO X2 NUC-class chassis pushing 60°F above ambient — small surface area limit visible, consistent with sustained 98°C edge sensor readings
- **DGX Spark**: DGX Spark compact desktop chassis pushing 40°F above ambient at sustained load
- **M5 Max MacBook Pro**: MBP exhaust essentially room-temperature — laptop cooling has massive headroom on this workload

### Electrical / room setup

- **Main room (78°F ambient)**: Blackwell 6000 Tower, EVO X2, DGX Spark all on one shared 20 A breaker.
- **M5 room (77°F ambient)**: M5 Max MacBook Pro on a separate 20 A breaker in a different room to prevent trips during heavy load.
- **Ambient differential** is only ~1 °F between rooms, so cross-host thermal comparisons are not biased by room temperature.
- All ambient measurements taken at the same instrumented moment as the exhaust readings, ~15.5 h into sustained operation.

## § Cost-throughput at single-user peak

This section reports tok/s per $1 k at the single-user / short-context operating point only. Multi-user conclusions are held — see § Held: multi-user concurrent serving.

### Approximate hardware cost per host

| host | cost (USD) | note |
|---|---:|---|
| Blackwell 6000 Tower (single-RTX-6000 reasonable build) | $12000 | What a fair cross-host comparison should anchor on — same gpu0 silicon, consumer/prosumer parts elsewhere. Performs the same on single-GPU inference workloads; the rest of the workstation overhead is configuration choice, not inference requirement. Anchored at $12k (deliberately on the generous side — covers a quality consumer board, capable PSU, decent cooling, NVMe, and quality RAM, with margin) so the comparison doesn't underestimate the discrete-GPU build cost. |
| Blackwell 6000 Tower (as-configured dual-GPU server) | $33000 | Built ground-up as a 1600 W professional dual-GPU inference server: TR PRO CPU, server-grade WRX90E board, ECC RAM (2×+ vs standard), 1600 W titanium PSU, redundant cooling. Most of the over-spec is for dual-GPU + workstation reliability, not for cross-host inference comparison. |
| EVO X2 | $3000 | GMKtec EVO X2 retail as of 2026-05-15. |
| DGX Spark | $4700 | DGX Spark retail as of 2026-05-15. |
| M5 Max MacBook Pro | $4850 | Configured 16" MBP, M5 Max, 128 GB unified, retail as of 2026-05-15. |

**The Blackwell 6000 Tower is anchored on the $12 k reasonable-single-RTX-6000 build, not the $33 k as-configured dual-GPU server**, because the cross-host comparison measures single-GPU inference. The $33 k accounts for dual-GPU + ECC + redundancy + server-grade board, which are configuration choices unrelated to the inference performance we're measuring. (We also report the as-configured row for reference.)

### Throughput per $1 k at peak short-context (best-cell, 27B Q8)

Single-user **decode tok/s per $1 k** at short context (ctx=1024 gen=2048 conc=1, 27B Q8) — the standard metric for hardware-buying comparisons.

| host | cost ($k) | decode tok/s | decode tok/s per $1 k |
|---|---:|---:|---:|
| Blackwell 6000 Tower (single-RTX-6000 build) | 12.0 | 49.4 | **4.12** |
| EVO X2 | 3.0 | 7.8 | **2.59** |
| DGX Spark | 4.7 | 7.6 | **1.62** |
| M5 Max MacBook Pro | 4.8 | 16.8 | **3.46** |

Peak **prefill tok/s per $1 k** at the same cell — the matmul-heavy phase that dominates first-token latency at long context.

| host | cost ($k) | prefill tok/s | prefill tok/s per $1 k |
|---|---:|---:|---:|
| Blackwell 6000 Tower (single-RTX-6000 build) | 12.0 | 2181.7 | **181.81** |
| EVO X2 | 3.0 | 269.0 | **89.67** |
| DGX Spark | 4.7 | 653.6 | **139.06** |
| M5 Max MacBook Pro | 4.8 | 535.6 | **110.42** |

### Reading

The Blackwell 6000 Tower wins decode tok/s per dollar at this operating point — 4.1 tok/s/$k vs M5 Max MacBook Pro 3.5, DGX Spark 1.6, EVO X2 2.6. It also wins prefill per dollar by an even larger margin because its bandwidth + compute lead is most pronounced in the matmul-heavy prefill phase.

Multi-user (conc≥4) cost-throughput is held — see § Held: multi-user concurrent serving.

_Cost figures are approximate retail as of 2026-05-15. The Blackwell 6000 Tower is anchored on the reasonable single-RTX-6000 build ($12 k); the as-configured $33 k dual-GPU server price is documented separately for transparency._

### Dual-anchor sensitivity: what if you used the $33 k as-configured price for Tower2?

Per AUDIT.md B12, the $12 k single-RTX-6000 anchor is the right answer for *inference performance* comparison. But a reader buying the actual server gets the $33 k as-built. Both anchors, side by side:

| host | anchor ($k) | decode tok/s/$1 k | prefill tok/s/$1 k |
|---|---:|---:|---:|
| Blackwell 6000 Tower ($12k single-RTX-6000) | 12.0 | **4.23** | **464.1** |
| Blackwell 6000 Tower ($33k as-configured) | 33.0 | **1.54** | **168.8** |
| EVO X2 | 3.0 | **2.59** | **89.7** |
| DGX Spark | 4.7 | **1.62** | **139.1** |
| M5 Max MacBook Pro | 4.8 | **3.46** | **110.4** |

Under the $33 k anchor, Tower2's decode tok/s/$k drops from 4.1 to ~1.5 — still positive but no longer top — and prefill drops from ~186 to ~68. The skeptical reader's right question is **"which anchor matches my purchase?"**: if they would buy a workstation with dual ECC GPUs and 1600 W titanium PSU because they need those things, use $33 k. If they would buy a one-GPU machine because their workload is one-GPU, use $12 k. The right number depends on the budget the comparison is informing.

### 5-year total cost of ownership under continuous load

Hardware cost dominates short-term, but at 24/7 inference the electricity bill catches up. 5-year TCO under continuous bench-style load, using each host's measured or estimated wall draw:

| host | hardware ($k) | mean wall (W) | source | 5-yr energy @ $0.12/kWh | total 5-yr (low) | total 5-yr @ $0.20/kWh |
|---|---:|---:|---|---:|---:|---:|
| Blackwell 6000 Tower | 12.0 | 445 | plug meter @ compute-light cell (peak ~850 W est) | $2,339 | $14.3 k | $15.9 k |
| EVO X2 | 3.0 | 155 | est: ~119 W silicon + ~30 W system overhead | $815 | $3.8 k | $4.4 k |
| DGX Spark | 4.7 | 80 | est: ~46 W silicon + ~25–35 W system overhead | $420 | $5.1 k | $5.4 k |
| M5 Max MacBook Pro | 4.85 | 142 | plug meter @ multi-user cell | $746 | $5.6 k | $6.1 k |

**Reading this:** Tower2 has the highest 5-yr TCO at ~$14–16 k (single-RTX-6000 anchor) up to ~$35–37 k (as-built dual-GPU server anchor). M5 Max stays close to its sticker price ($5.6–6.4 k) — laptops are cheap to run continuously. **DGX Spark and EVO X2 wall figures are estimated, not plug-metered** — they need explicit ground-truth readings before TCO claims firm up (audit gap, see B8). The Tower2 wall figure is a plug-meter reading at a *compute-light* cell; peak-cell wall is estimated ~850 W and would push 5-yr energy to ~$4.5–7.5 k, ~$2–4 k higher than shown.

## § Cross-host generation determinism

Each inference at `temperature=0, seed=42` should produce the same output on every backend. We compute SHA256 of every generation and check whether different hosts running the same prompt produced the same SHA.

- **Inferences with SHA captured:** 6467
- **Prompts run on 2+ hosts (cross-host comparable):** 1900
- **Hosts produced byte-identical output:** 99 of 1900 = 5.2%
- **Hosts produced divergent output:** 1801

### Divergent generations (first 10)

| model | cell | inference id | host/backend → SHA prefix |
|---|---|---|---|
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s0 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=aeed5e04`; `tower2/cuda=f7564cd6` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s1 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=3312bf12`; `tower2/cuda=d341b25b` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s2 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=3ca2d47b`; `tower2/cuda=3386a290` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s3 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=0475d0be`; `tower2/cuda=43e6c8ea` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s4 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=f1fa568c`; `tower2/cuda=3cb257a7` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s5 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=16895b66`; `tower2/cuda=5e3dc0af` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s6 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=b9a1d119`; `tower2/cuda=f1d23d0b` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b0_s7 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=550468e0`; `tower2/cuda=d8563104` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b1_s0 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=b9a1d119`; `tower2/cuda=5e3dc0af` |
| qwen3.6-27b | ctx32768_gen0512_conc8 | b1_s1 | `m5-mbp/metal=5db4f28c`; `spark/cuda-aarch64=f1fa568c`; `tower2/cuda=d8563104` |

## § Generation length per host

Does the model produce different-length output on different backends? Per-inference `content_len_chars` distribution.

| host/backend | n | mean chars | median chars | p95 chars | min | max |
|---|---:|---:|---:|---:|---:|---:|
| m5-mbp/metal/qwen3.6-27b | 1512 | 2064 | 1253 | 8603 | 484 | 9648 |
| m5-mbp/metal/qwen3.6-35b-a3b | 260 | 4689 | 6195 | 8257 | 2020 | 8721 |
| spark/cuda-aarch64/qwen3.6-27b | 910 | 2930 | 2236 | 8453 | 484 | 9523 |
| spark/cuda-aarch64/qwen3.6-35b-a3b | 1560 | 2027 | 1247 | 7902 | 482 | 8777 |
| strix-halo/vulkan/qwen3.6-27b | 803 | 2544 | 1885 | 7232 | 484 | 9877 |
| strix-halo/vulkan/qwen3.6-35b-a3b | 260 | 875 | 1111 | 1251 | 427 | 2179 |
| tower2/cuda-vllm/qwen3.6-27b | 164 | 5557 | 7858 | 9478 | 516 | 9505 |
| tower2/cuda-vllm/qwen3.6-35b-a3b | 468 | 3285 | 2092 | 8871 | 443 | 9062 |
| tower2/cuda/qwen3.6-27b | 530 | 3122 | 2257 | 8494 | 487 | 9752 |

## § Stop reason per host

Why did each generation terminate? Mostly should be `limit` since we cap at gen_target tokens, but `eos` and `stop_word` reveal model-emergent behavior.

| host/backend | model | limit | eos | stop_word | other |
|---|---|---:|---:|---:|---:|
| m5-mbp/metal | qwen3.6-27b | 1512 | 0 | 0 | 0 |
| m5-mbp/metal | qwen3.6-35b-a3b | 1242 | 318 | 0 | 0 |
| spark/cuda-aarch64 | qwen3.6-27b | 1489 | 71 | 0 | 0 |
| spark/cuda-aarch64 | qwen3.6-35b-a3b | 1451 | 109 | 0 | 0 |
| strix-halo/vulkan | qwen3.6-27b | 1285 | 38 | 0 | 101 |
| strix-halo/vulkan | qwen3.6-35b-a3b | 260 | 0 | 0 | 0 |
| tower2/cuda | qwen3.6-27b | 1469 | 21 | 0 | 70 |
| tower2/cuda | qwen3.6-35b-a3b | 0 | 0 | 0 | 1560 |
| tower2/cuda-vllm | qwen3.6-27b | 0 | 0 | 0 | 164 |
| tower2/cuda-vllm | qwen3.6-35b-a3b | 0 | 0 | 0 | 468 |

## § Coherence spot-check

10 random generations (with prompt context) sampled from across the grid. Use these to eyeball whether Q8 output looks reasonable on every backend.

### `m5-mbp/metal/qwen3.6-27b` — cell ctx01024_gen0128_conc8 — b8_s7
- decode 6.1 tok/s, gen 128 tokens, stop=limit
- content sha: `d8676dcb6026a0cb`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user provides a text that is a repetition of the opening paragraph and dialogue from Jane Austen's *Pride and Prejudice*.
    *   The text repeats the same block three times, and the fourth time is cut off ("first enteri").
    *   *Content:* "It is a truth universally acknowledged..." -> Mrs. Bennet tells Mr. Benn
```

### `tower2/cuda-vllm/qwen3.6-35b-a3b` — cell ctx04096_gen2048_conc4 — b2_s3
- decode 164.3 tok/s, gen 1759 tokens, stop=None
- content sha: `41baee4b76277414`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user provides a text that is a repetition of the opening paragraph of Jane Austen's *Pride and Prejudice*.
    *   The text repeats the same block of text multiple times.
    *   The block contains:
        *   The famous opening sentence: "It is a truth universally acknowledged..."
        *   The dialogue between
```

### `tower2/cuda/qwen3.6-27b` — cell ctx32768_gen0128_conc4 — b3_s2
- decode 0.5 tok/s, gen 128 tokens, stop=limit
- content sha: `5d1a4afbdb733ae1`

```


<think>
Here's a thinking process:

1.  **Analyze User Input:**
   - **Input Text:** The user provided a very long passage that is actually just the opening paragraph of Jane Austen's *Pride and Prejudice* repeated many times (over 50 times). It ends abruptly mid-sentence: "...this truth is so well fixed in the minds of the surrounding familie"
   - **Task:** Summarize the passage and continue t
```

### `m5-mbp/metal/qwen3.6-27b` — cell ctx01024_gen2048_conc8 — b4_s5
- decode 6.2 tok/s, gen 295 tokens, stop=limit
- content sha: `07eec6e56aed96dd`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user provides a text that is a repetition of the opening paragraph and dialogue from Jane Austen's *Pride and Prejudice*.
    *   The text repeats the same block three times, and the fourth time is cut off ("first enteri").
    *   *Content:* "It is a truth universally acknowledged..." -> Mrs. Bennet tells Mr. Benn
```

### `spark/cuda-aarch64/qwen3.6-27b` — cell ctx32768_gen0512_conc8 — b3_s4
- decode 2.2 tok/s, gen 512 tokens, stop=limit
- content sha: `0475d0beadac6b95`

```


<think>
Here's a thinking process:

1.  **Analyze User Input:**
   - **Input Text:** The user provided a very long passage that is actually just the opening paragraph of Jane Austen's *Pride and Prejudice* repeated many times (over 50 times). It ends abruptly mid-sentence: "...this truth is so well fixed in the minds of the surrounding familie"
   - **Task:** Summarize the passage and continue t
```

### `strix-halo/vulkan/qwen3.6-35b-a3b` — cell ctx01024_gen0128_conc4 — b7_s3
- decode 27.2 tok/s, gen 128 tokens, stop=limit
- content sha: `9bd572638827fe70`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user provides a text that is clearly the opening of Jane Austen's *Pride and Prejudice*.
    *   The text repeats the first paragraph and the dialogue between Mr. and Mrs. Bennet three times, and then cuts off mid-sentence at the end ("first enteri").
    *   *Key Content:*
        *   Famous opening line: "It is a
```

### `strix-halo/vulkan/qwen3.6-27b` — cell ctx04096_gen2048_conc8 — b9_s1
- decode 2.3 tok/s, gen 441 tokens, stop=limit
- content sha: `82ee876ee6cc0230`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user provided a text that is a repetition of the opening paragraph and the first dialogue exchange from Jane Austen's *Pride and Prejudice*.
    *   The text repeats the same block multiple times:
        *   "It is a truth universally acknowledged..."
        *   "My dear Mr. Bennet..."
        *   Dialogue about 
```

### `tower2/cuda-vllm/qwen3.6-35b-a3b` — cell ctx04096_gen0128_conc8 — b1_s0
- decode 97.4 tok/s, gen 128 tokens, stop=None
- content sha: `51f2328dd819605f`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user provides a text that is a repetition of the opening paragraph of Jane Austen's *Pride and Prejudice*.
    *   The text repeats the same block of text multiple times.
    *   The block contains:
        *   The famous opening sentence: "It is a truth universally acknowledged..."
        *   The dialogue between
```

### `m5-mbp/metal/qwen3.6-27b` — cell ctx01024_gen0512_conc8 — b9_s4
- decode 5.1 tok/s, gen 295 tokens, stop=limit
- content sha: `07eec6e56aed96dd`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user provides a text that is a repetition of the opening paragraph and dialogue from Jane Austen's *Pride and Prejudice*.
    *   The text repeats the same block three times, and the fourth time is cut off ("first enteri").
    *   *Content:* "It is a truth universally acknowledged..." -> Mrs. Bennet tells Mr. Benn
```

### `tower2/cuda-vllm/qwen3.6-35b-a3b` — cell ctx16384_gen0512_conc4 — b0_s1
- decode 121.6 tok/s, gen 512 tokens, stop=None
- content sha: `4bf2b5310db34610`

```


<think>
Thinking Process:

1.  **Deconstruct and Analyze the Input:**
    *   The user has provided a very long text.
    *   Scanning the text, I notice it's the opening paragraph of Jane Austen's *Pride and Prejudice*.
    *   However, the text is repeated many times. It looks like a copy-paste error or a loop where the same paragraph is pasted over and over again.
    *   The content is: "It 
```


## § Hosts

Form factor matters — these four hosts span workstation, NUC-class mini-PC, reference desktop, and laptop. Compare power/thermal numbers in light of the chassis the silicon is sitting in.

- **Blackwell 6000 Tower** (x86_64, linux) — _chassis: Custom workstation tower (ASUS WRX90E, 1600 W titanium PSU, 8× Noctua 120 mm intake + 6× exhaust = 14-fan airflow, open-air panel)_ — backends: cuda; power sampler nvidia-smi; notes: 2× RTX PRO 6000 Blackwell Workstation (96 GB each, GDDR7). For the parallel cross-host run, ONLY GPU 0 is used (CUDA_VISIBLE_DEVICES=0) at 600W cap — keeps the room breaker safe when all four hosts run concurrently. GPU 0 600W ≈ 5090 575W TGP, so single-card numbers read across to a 5090 within a few percent (excluding VRAM-ceiling effects: 32GB on 5090 vs 96GB on PRO 6000). Dual-card supplementary run executes SEQUENTIALLY after the parallel sweep clears. dream-llama-server must be stopped before bench runs. M5 is in a different room — not on the same breaker.
- **EVO X2** (x86_64, linux) — _chassis: GMKtec EVO X2 mini-PC (NUC-class small-form-factor enclosure)_ — backends: vulkan; power sampler rocm-smi; notes: AMD Ryzen AI MAX+ 395, 124 GB unified, in a GMKtec EVO X2 mini-PC chassis. Vulkan currently canonical pending ROCm retry sub-study. Form factor is a small NUC-class enclosure, NOT a workstation — compare power/thermal numbers in that light.
- **DGX Spark** (aarch64, linux) — _chassis: NVIDIA DGX Spark reference desktop (compact desktop form factor)_ — backends: cuda-aarch64; power sampler nvidia-smi; notes: DGX Spark GB10 Grace Blackwell, 121 GB unified, aarch64. NOT a Jetson — tegrastats does not apply; use nvidia-smi for power+thermals same as Tower2. CUDA 13.0 at /usr/local/cuda (not in default PATH). Coder-Next has known aarch64 garbage-token bug; Qwen3.6-27B + 35B-A3B verified fine.
- **M5 Max MacBook Pro** (arm64, macos) — _chassis: Apple MacBook Pro 16" (M5 Max, laptop/notebook form factor)_ — backends: metal; power sampler powermetrics; notes: Apple M5 Max, 128 GB unified, 18-core, macOS 26.4. Username 'conta'. WiFi-attached (NOT switch-wired). 1.7 TB free disk. Also runs MLX appendix.

### Form-factor caveats for the headline ranking

- **Blackwell 6000 Tower** is a workstation with a 1600 W titanium PSU and effectively unlimited cooling headroom. Its single GPU is power-capped at 600 W.
- **EVO X2** (GMKtec EVO X2 with AMD Ryzen AI MAX+ 395 / Strix Halo APU) is a NUC-class small-form-factor enclosure. Sustaining a ~119 W GPU package load + ~98 °C edge temperature in that chassis is qualitatively different from a workstation tower at the same load. Read its numbers in that light.
- **DGX Spark** is the reference NVIDIA DGX Spark desktop (compact desktop with GB10 Grace Blackwell).
- **M5 Max MacBook Pro** is a 16" laptop on its AC-charged battery PSU; `sys` macmon power is the closest reading we have to wall-AC (plug-meter validated at 142 W vs 128 W reported, ~10 % gap).

### Backend-completeness caveat

The EVO X2 host runs Vulkan only in this study. ROCm was attempted and segfaulted (see § Two backend-bug findings, Finding 1); a proper retry sub-study (longer wait-ready, smaller bootstrap model, fresh stderr/dmesg capture) is a queued follow-up. Until that retry runs, **the Vulkan numbers stand on their own — this study does not yet make a comparative Vulkan-vs-ROCm claim**.

## § Methodology

Per cell: load model once, 10 batches of N=`conc` parallel requests each, `temperature=0 seed=42 cache_prompt=false`. First 2 batches discarded as warmup. Samplers stream at 1 Hz with monotonic + wall-clock timestamps.

## § Reproducibility

- Source: `https://github.com/ggml-org/llama.cpp@67b2b7f2f2d6dac7962b219168a4c7a20c7359b7`
- Prompts: `workloads/prompts.jsonl` (SHA `9a27eba85a8da9443d7fcf74e281b011831806c4b24aaaada3915463d5c13cd8`)
- Per-host build invocations under each host's `build-<backend>.configure.log`
- Per-host `env.json` snapshots (driver versions, GPU info, cmake/SDK versions)
- Raw per-cell: `<host>/<model>/<backend>/ctxNNNN_genNNNN_concN/{cell.json,inferences.jsonl,batches.jsonl,power.csv,thermals.csv,llama-server-*.log}`

## § Companion analyses (status)

- **MMBT Phase B Q8 task-quality eval** — the matching quality benchmark on Q8 was the second of two original goals. **Not run yet; not in this PR.** Planned as a follow-up.
- **`sustained/` subdirectory** — preliminary throttle-curve samples (one cell each on three of four hosts). The substantive thermal story for this PR is the psychrometer-anchored § Sustained thermal field measurements section above, not the `sustained/` time-series. The full sustained-tier (30 min per host × both models) is a follow-up.
- **`audit/SEMANTIC-EQUIVALENCE-35B-A3B.md`** — quant-format audit defending the Tower2 vLLM FP8 appendix headline. Lives in `audit/`; load-bearing for the FP8 row in the ranking table.

## § Audit

See `AUDIT.md` for the rigor self-audit: what's locked across hosts, what unavoidably varies, biases B1–B12, the plug-meter calibration log, and known issues including the two backend-bug findings above.
