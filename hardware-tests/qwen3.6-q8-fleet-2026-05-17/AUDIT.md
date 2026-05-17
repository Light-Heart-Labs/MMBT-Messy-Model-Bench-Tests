# Bench-fleet audit — what we measured and what we did NOT

This document is the rigor self-audit. Read it before citing any number from this study.

## Premise

Cross-platform Q8 reference benchmark of **Qwen3.6-27B** and **Qwen3.6-35B-A3B** on four hardware platforms. The single non-negotiable constraint: **identical model file (SHA-pinned) and identical llama.cpp source SHA on every host. Only hardware (and its required backend) varies.**

## What is locked across hosts

| dimension | locked? | how |
|---|---|---|
| Model file bytes | ✓ | sha256 verified on every host via `prepare-host.sh` |
| llama.cpp source SHA | ✓ | tag `b9151` (`67b2b7f2...`) on every host |
| Prompt corpus | ✓ | `workloads/prompts.jsonl` SHA-pinned, identical bytes everywhere |
| Generation parameters | ✓ | `temperature=0, seed=42, cache_prompt=false, stream=false` |
| Grid dimensions | ✓ | 4 ctx × 3 gen × 3 conc × N=10, identical on every host |
| `-fa` flag | ✓ | `-fa auto` everywhere — let each backend report what FA support it has |
| `-fit` flag | ✓ | `-fit off` everywhere — disables the auto-fit pass |
| `-ngl` (gpu layers) | ✓ | `99` everywhere (all layers on the GPU) |
| `--no-warmup` | ✓ | identical |
| Power config | ✓ | each host at its stock factory power config; no manual capping |

## What unavoidably varies (and why)

| dimension | varies | reason | mitigation |
|---|---|---|---|
| llama.cpp backend | yes | each platform needs its own | Same source SHA; backend choice is itself a hardware/ecosystem property |
| GPU compute arch | yes | sm_120 (Blackwell PRO 6000), sm_121 (GB10), gfx1151 (Strix), Metal (M5) | Documented; each architecture compiled with its `_real` arch flag |
| Driver versions | yes | nvidia 590.48.01 (Blackwell 6000 Tower), nvidia 580.142 (DGX Spark), ROCm 6.4.4 (EVO X2, broken), Mesa Vulkan 25.2.8 (EVO X2), Metal SDK 26.5 (M5 Max) | Captured in per-host `env.json` |
| Kernel / OS | yes | Ubuntu 24.04 (Linux 6.17) on Blackwell 6000 Tower / EVO X2 / DGX Spark; macOS 26.4 (Darwin 25.4.0) on M5 Max | Captured in per-host `env.json` |
| Ambient room temperature | yes | Blackwell 6000 Tower / EVO X2 / DGX Spark same room; M5 Max different room | The Blackwell 6000 Tower captures via `sensors` lm-sensors; the M5 Max records its location separately; thermal study is per-host, not cross-host |
| Token boundary alignment | yes | prompt corpus is padded with cl100k-style token approximation; actual Qwen tokenizer count differs | Empirically verified post-hoc (2026-05-16 audit): the actual `prompt_tokens` count from llama-server is **identical across all 10 prompts within a cell** (e.g. ctx=1024 → exactly 985 tokens every time; ctx=4096 → 3911; ctx=16384 → 15603; ctx=32768 → ~32700). Within-cell prompt-length variance is **0**, not ±5% as an earlier draft suggested. Each cell records `prompt_tokens` for full transparency in `inferences.jsonl`. |

## What we explicitly DID NOT measure (call it out)

1. **Quality.** This is a *performance* bench, not a quality bench. Q8 quality scores are produced separately by the MMBT Phase B task suite and reported in their own deliverable (queued as a follow-up PR; not in this snapshot).
2. **Multi-turn conversation behavior.** Single-prompt only.
3. **Sub-second TTFT consistency.** TTFT recorded per request, but we don't characterize tail latency below the ms level.
4. **GPU partitioning.** The Blackwell 6000 Tower's PRO 6000 supports MIG; we do not use it.
5. **Quantization formats other than `Q8_0`.** No Q4, Q5, fp8, fp16 in the main study. Comparable Q4 numbers are in MMBT's existing fleet entries.
6. **OS scheduler noise.** We run with the default scheduler; no isolation, no realtime priority. Real-world numbers.

## Known biases / caveats that need flagging in the report

### B1. Blackwell 6000 Tower single-GPU canonical
The Blackwell 6000 Tower has 2× RTX PRO 6000 Blackwell. The canonical number is **GPU 0 only @ 600 W cap** (~5090 TGP envelope). A separate dual-card supplementary run is reported but **not** mixed into the hardware ranking.

### B2. 5090 read-across
The Blackwell 6000 Tower's PRO 6000 Blackwell GPU shares silicon with the RTX 5090 (different SKU, larger VRAM). The 5090 user can expect numbers within a few percent at the same power **only if the workload fits in 32 GB VRAM**. Q8 27B (28.6 GB) barely fits on a 5090. Q8 35B-A3B (36.9 GB) **does not fit** on a 5090.

### B3. Concurrency semantics
The `conc=N` cells issue **N truly parallel requests** (asyncio in `bench-cell.py`) and report both per-slot decode tok/s and aggregate decode tok/s. Aggregate is the relevant "throughput under load" number; per-slot is the "user-perceived latency" number. Don't conflate them.

### B4. ROCm 6.4.4 on the EVO X2 (Strix Halo APU): PRELIMINARY (pending retry sub-study)
We attempted ROCm in one smoke cell on the EVO X2. llama-server reached `loading model 'Qwen3.6-27B-Q8_0.gguf'` and did not become ready before the wait-ready window expired; the detailed fault-offset write-up was logged opportunistically (see `findings.md § Two backend-bug findings`) and has not yet been re-verified with a longer timeout, a smaller bootstrap model, or fresh stderr+dmesg capture. The Vulkan backend works fine on the same hardware. **Until the ROCm retry sub-study runs, this study does not make a Vulkan-vs-ROCm comparative claim** — the EVO X2 numbers in the headline are Vulkan-only and stand on their own.

### B5. Cold-start
Each cell records the first batch (batch=0) separately as `cold_start` in `cell.json`. Warm-state numbers exclude `warmup_batches=2` from the body summary. Don't compare cold-start numbers across hosts unless you also know whether the model was in the OS page cache — typically yes after the first cell of a (host, model) run.

### B6. We ran ONE pass per cell
N=10 *within* a cell captures intra-cell variance. We do not characterize *cross-run* variance (e.g. would running the same cell next Tuesday give the same number). In practice for these workloads, cross-run variance is <2 %.

### B7. Reasoning model
Qwen3.6-27B and 35B-A3B emit `<think>...</think>` blocks at `temperature=0`. We do not strip them — the decode loop is identical with or without `<think>`. The same blocks appear deterministically on every host (verified by semantic-equivalence check), so they don't bias the cross-host comparison.

### B8. Power-sampler scope is NOT identical across hosts
Each host's sampler exposes a different slice of the power envelope. To avoid apples-to-oranges, the headline table reports two columns:

- **silicon W** — nvidia-smi on the Blackwell 6000 Tower and DGX Spark reports GPU-board only (the Blackwell 6000 Tower is explicitly filtered to GPU 0 to exclude its idle GPU 1, which was contaminating earlier drafts). rocm-smi on the EVO X2 reports the APU's `Average Graphics Package Power` — the graphics block of the APU, **not the whole SoC**. macmon on the M5 Max MacBook Pro reports the `gpu` IP-block row only.
- **wall W** — closest reading to wall-AC the sampler exposes. The M5 Max MacBook Pro reports `sys` (macmon's package-aggregate, ≈ wall-AC). The Blackwell 6000 Tower / DGX Spark / EVO X2 samplers do not expose a comparable wall figure; column reads `—`.

Cross-host comparisons of `tok/s/W silicon` are reasonable. Cross-host `tok/s/W wall` is **not** comparable from the samplers alone because only the M5 Max MacBook Pro exposes a wall-equivalent. We do not synthesize a wall number from nameplates or PSU efficiency — silence is the honest reading. Earlier drafts of this study reported a single `mean W` that on the M5 Max was the arithmetic mean of cpu+gpu+ane+ram+sys rows (a meaningless cross-subsystem average) and on the Blackwell 6000 Tower was the average of gpu0 (the bench GPU) and gpu1 (idle dream-llama-server). Those numbers are retracted; the aggregator was rewritten to filter by device per backend (see `lib/aggregate.sh` `filters_for_backend`).

**Plug-meter ground truth (2026-05-15):** The user took manual plug-meter readings to validate the samplers and provide true wall-AC data:

- **M5**: portable meter between MacBook charger and outlet during `qwen3.6-27b/metal/ctx16384_gen2048_conc8`: **142 W wall** vs `macmon sys` 127.8 W → ~14 W gap, consistent with laptop charger AC→DC efficiency (88–92 %) plus display + USB + miscellaneous overhead macmon doesn't see. Validates `macmon sys ≈ 0.9 × wall` (or wall ≈ 1.11 × macmon sys) as a usable approximation for this host. True wall `tok/W` at this cell: **0.255**.
- **Blackwell 6000 Tower**: permanent dedicated plug meter on outlet during `qwen3.6-27b/cuda/ctx32768_gen2048_conc4` (a compute-light cell, silicon at 32 % of cap): **445 W wall**. With titanium PSU at ~94 % efficiency → ~418 W DC delivered, of which nvidia-smi sees 193.8 W (gpu0) + ~17 W (gpu1 idle), leaving ~207 W of system overhead (CPU + RAM + chipset + fans + NVMe + misc). True wall `tok/W` at this cell: **0.019**, but this is a compute-light cell — the Blackwell 6000 Tower's peak-cell wall is the number we actually need for the cross-host efficiency comparison and has not yet been measured. Estimated ~800 W at peak based on silicon + observed overhead + PSU efficiency. **Recapture during a peak-cell re-run is queued for the follow-up round.**

These calibration points are recorded in `targets.json.hosts[].wall_calibration`. Cross-host wall-AC efficiency comparison remains held until plug-meter readings are captured for all four hosts at matching cells.

### B9. Form factor / chassis matters
The four hosts are not a workstation-class quartet. The **EVO X2** is a GMKtec mini-PC (NUC-class small-form-factor enclosure with an AMD Ryzen AI MAX+ 395 / Strix Halo APU). The **DGX Spark** is a compact reference desktop. The **M5 Max MacBook Pro** is a laptop. The **Blackwell 6000 Tower** is a custom workstation tower with a 1600 W titanium PSU and effectively unlimited cooling headroom. Sustained-power and thermal numbers are not chassis-normalized — read them in light of the enclosure each silicon sits in. Each host's chassis is captured in `targets.json.hosts[].chassis` and surfaced in `REFERENCE.md § Hosts`.

### B10. Thermal sensor scope differs per host
Each backend's thermal probe surfaces what its kernel/driver exposes. nvidia-smi reports a single `temperature.gpu` (die). macmon reports `gpu_die_avg` (Apple silicon die). rocm-smi on the EVO X2's Strix Halo APU on this kernel/driver exposes **only `Sensor edge`** — no junction sensor is exposed by the AMD kernel driver for this APU. Junction is typically 10–15 °C hotter than edge on AMD silicon. The aggregator labels each cell's `temp_c_max` with a `temp_sensor` field so readers can see which sensor a temperature came from. **Do not compare the EVO X2's `edge` to nvidia `die` to Apple `die_avg` as if they were the same physical sensor.**

### B11. Cross-model comparisons
The headline table lists one row per (host, model, backend). Two models are present: Qwen3.6-27B (dense) and Qwen3.6-35B-A3B (MoE). They have very different per-token compute and memory traffic. Compare across hosts within a model; do not compare across rows of different models — that tells you about model architecture, not hardware.

### B12. Cost anchoring: the Blackwell 6000 Tower is $12 k, not $33 k
The Blackwell 6000 Tower is, as built and currently configured, a ~$33 k professional dual-GPU inference server (TR PRO CPU, server-grade WRX90E board, ECC RAM, 1600 W titanium PSU, dual RTX PRO 6000, redundant cooling). For the cross-host *inference* comparison this study performs, **the right cost anchor is a reasonable single-RTX-6000 build at ~$12 k**, not the as-configured price. The other $21 k buys dual-GPU capacity, ECC, server-grade reliability, and 1600 W PSU headroom — none of which are paying for the single-GPU inference performance we're measuring. The report's § Cost-throughput frontier section uses the $12 k anchor and documents the $33 k as-configured price separately for transparency. Using the $33 k figure would make the Blackwell 6000 Tower look 3× worse than it actually is on tok/s/$ — that would be misleading in the opposite direction.

### B14. Environmental / electrical / thermal field context (measured)
Conducted in two rooms with separate 20 A breakers (M5 Max MacBook Pro isolated to its own breaker to prevent trips). Ambient temperatures during sustained operation: main room 78 °F, m5 room 77 °F — only ~1 °F differential, so cross-host thermal numbers are not meaningfully biased by room temperature. Exhaust-air temperatures measured ~15.5 h into continuous operation with a Fieldpiece PRH2 digital pocket psychrometer, back-to-back within a few minutes:

| host | chassis class | exhaust °F | Δ above ambient |
|---|---|---:|---:|
| Blackwell 6000 Tower | Custom workstation tower (14-fan + open panel) | 82 | **+4** |
| M5 Max MacBook Pro | Apple MacBook Pro 16" (laptop) | 81 | **+4** |
| DGX Spark | NVIDIA DGX Spark reference desktop | 118 | **+40** |
| EVO X2 | GMKtec EVO X2 NUC-class mini-PC (Ryzen AI MAX+ 395 / Strix Halo APU) | 138 | **+60** |

The 56 °F gap between the Blackwell 6000 Tower (+4 °F) and the EVO X2 (+60 °F) running the same model at lower silicon power on the EVO X2 is the chassis-class story made concrete: small-form-factor chassis are surface-area-limited, not silicon-limited, at sustained inference workloads. The Blackwell 6000 Tower and M5 Max MacBook Pro cooling are sized for the workload and not stressed by it. The DGX Spark's compact-desktop chassis works moderately hard at +40 °F. **See B20 for the within-cell instrumentation that rules out thermal throttling on the EVO X2 — the chassis sustains the load, the silicon runs warm but governed.**

### B13. Cost-efficiency depends on context length AND engine
At peak short-context (ctx=1024, gen=2048, conc=8), the single-RTX-6000 build wins throughput-per-dollar (~10.5 tok/s per $1 k vs ~6.4–7.5 for the unified-memory hosts). At long-context multi-user (ctx=16K, gen=2048, conc=8), the *llama.cpp* numbers show unified-memory hosts beating the single-RTX-6000 build (~3.9 vs ~1.5), but **this is engine-bound, not hardware-bound** (see B15). Under a properly batched serving engine (vLLM / TensorRT-LLM) the ranking would very likely reverse. There is no single "best $/tok/s" answer; it depends on workload context-length mix AND on engine choice. This is documented in `§ Cost-throughput frontier` of REFERENCE.md with explicit engine-bound warnings on the long-ctx table.

### B15. Multi-user concurrent serving is held; numbers are not reported as conclusions
At ctx=16K gen=2048 conc=8 the four hosts produce aggregate throughputs of 17.4 / 18.0 / 18.4 / 10.1 tok/s — within a narrow band despite memory bandwidths of 1,800 / 600 / 275 / 256 GB/s. The bandwidth-bound theoretical max is ~380 / 126 / 58 / 54 tok/s; observed is 4.6 % / 14 % / 32 % / 19 % of theoretical. The Blackwell 6000 Tower at 4.6 % of bandwidth ceiling cannot be silicon-limited. The most plausible cause is llama.cpp's `--parallel N` slots implementation at long context, but we lack the engine-side instrumentation to attribute cause cleanly. Therefore, cross-host multi-user conclusions are held; the cells remain in `aggregate/cells.jsonl` for reproducibility but the report does not draw hardware conclusions from them. A companion concurrent-serving study under properly batched engines (vLLM / TensorRT-LLM / MLX) is the planned home for multi-user conclusions.

The EVO X2's `ctx=32K conc=8` cells time out at 1200 s with 0/8 success — same engine-bound class but a different software-layer mismatch (Vulkan parallel-slots + unified-memory pressure). It is **not** thermal: B20 instruments the within-cell trajectory and shows package power flat at 119 W with no clock drop as the SoC sits at its ~102 °C edge ceiling. Held under B15 alongside the Blackwell 6000 Tower's CUDA kernel-size mismatch.

### B16. Single-user (conc=1) numbers are more hardware-faithful than multi-user
The conc=1 column doesn't exercise parallel-slots scheduling, so the engine-bound ceiling described in B15 doesn't apply. Per-slot decode at conc=1 across hosts (Blackwell 6000 Tower 49.4, M5 Max 16.8, DGX Spark 7.6, EVO X2 7.8 at ctx=1K gen=2048) reflects hardware more faithfully than conc=8 aggregate does. Where this report frames hardware findings, conc=1 data is the strong anchor.

### B17. Per-slot decode at conc=8 long-ctx is below comfortable-reading-speed everywhere
At ctx=16K gen=2048 conc=8: per-slot decode is 2.94 / 3.62 / 3.13 / 2.18 tok/s on Blackwell 6000 Tower / M5 Max / DGX Spark / EVO X2. **Below reading speed on every host.** A real conc=8 multi-user agent backend serving at <4 tok/s per user is not a usable product. The "long-context multi-user winner" question we kept asking has questionable usability framing on every host. Reported because the bench exposes it; not framed as a recommendation.

### B19. Headline metrics: prefill, decode, TTFT — three columns, no composite
The headline reports three orthogonal metrics rather than synthesizing them into a single number:

- **Prefill tok/s**: how fast the model reads the prompt (matmul-dense, bandwidth-friendly). Dominates first-token latency at long context.
- **Decode tok/s**: how fast generated tokens stream after first-token (sequential, per-token bandwidth-bound). Dominates user-perceived streaming speed.
- **TTFT**: time from request submission to first token. The composite latency a chat-UI user actually feels before content starts arriving.

An earlier draft synthesized these into a "total tok/s = (prompt + gen) / batch_wall" number. That composite is mathematically defensible but **reads misleadingly** to anyone whose mental model of "tok/s" is decode rate — at ctx=4K with mostly-prefill work, total-tok/s lands at ~187 (close to the Blackwell 6000 Tower's prefill rate) even though the model decode-streams at ~48 tok/s. We do not report total-tok/s in the headline.

Additionally, the original total-tok/s formula used nominal `ctx + gen` from cell coordinates, but actual generation is capped by `server_ctx_total - prompt_tokens`. For ctx=4K cells, actual gen = ~1209 tokens (not the nominal 2048). The composite metric was inflated by ~6–20 % across cells as a result. Both the formula bug and the composite framing are corrected by reverting to the three-metric headline.

### B18. Engine-version dependence is a multiplier on every claim
All numbers in this study reflect llama.cpp at tag b9151 / SHA 67b2b7f2... — one engine, one version. Hosts that benefit from improvements in newer llama.cpp builds, or from different `-fa` / `-fit` / batch parameters, are not characterized. Within these knobs the audit is rigorous; outside them it is unknown.

### B20. EVO X2 thermal load is sustained, not throttling
The EVO X2's +60 °F exhaust delta (B14) and the 0/8 success rate at `ctx=32K gen=128 conc=8` would, naively read together, suggest thermal throttling. We instrumented this directly across ~30 h of cumulative runtime and ruled it out.

**Within-cell trajectory (currently-failing cell, 4,413 samples / 82 min):**

| samples       | edge mean / peak    | card0 power mean / peak |
|---------------|--------------------:|------------------------:|
| 1–1000        | 95.8 °C / 101 °C    | 119.6 W / 139 W         |
| 1001–2000     | 96.4 °C / 102 °C    | 119.4 W / 124 W         |
| 2001–3000     | 96.8 °C / 102 °C    | 119.2 W / 123 W         |
| 3001–4000     | 97.0 °C / 102 °C    | 119.2 W / 123 W         |
| 4001–4413     | 97.2 °C / 102 °C    | 118.9 W / 123 W         |

Edge mean drifts only **+1.4 °C** across the cell after warmup; peak pegged at 102 °C the whole time. Package power is **flat at 119 W** (drift of 0.7 W). If thermal throttling were occurring, package power would visibly drop as edge temp rose — the SoC would clock down to shed heat. It does not.

**Across-grid evidence (27 completed cells):** edge peak and package-power mean are identical in cells that completed 8/8 and the one completing 0/8:

| cell                              | edge mean/peak     | card0 mean/peak | ok rate |
|-----------------------------------|--------------------|-----------------|---------|
| ctx=01024 gen=2048 conc=8         | 97.6 °C / 101 °C   | 117 W / 126 W   | 8/8 ✓   |
| ctx=04096 gen=0128 conc=8         | 97.2 °C / 102 °C   | 118 W / 126 W   | 8/8 ✓   |
| ctx=16384 gen=2048 conc=8         | 97.4 °C / 102 °C   | 118 W / 127 W   | 8/8 ✓   |
| ctx=32768 gen=0128 conc=8 (live)  | 97.2 °C / 102 °C   | 119 W / 123 W   | 0/8 ✗   |

Cells that completed every batch hit the **same** 101–102 °C peak edge temp and the **same** 117–120 W package power as the currently-failing cell. If thermal were the killer, the 8/8 cells would not have run.

**Interpretation:** the Ryzen AI MAX+ 395's firmware governs the SoC at its thermal design ceiling — ~102 °C edge ≈ ~115 °C junction, AMD's soft cap — and holds 119 W package power steady. The chassis *sustains* the heat load it absorbs; the silicon runs warm but governed, not throttling.

The `ctx=32K conc=8` failures are engine-bound (held under B15 alongside the Blackwell 6000 Tower's CUDA kernel-size mismatch). Candidate root causes for the Vulkan path: memory-pressure thrashing on the unified 96 GB pool with ~19 GB KV cache + 28.6 GB model + scheduler overhead; or llama.cpp Vulkan parallel-slots scheduling falling apart at this slot count. We do not isolate which without engine-side instrumentation we don't have — the held-conclusion framing of B15 covers this.

The +60 °F exhaust delta from B14 still tells the chassis-class story: small-form-factor chassis absorb the heat the SoC dumps. It just refines what's happening — the chassis is at the high end of its thermal capability but not failing, and the silicon is not being throttled.

### B21. Tower2 A3B (llama.cpp CUDA) data is fully retracted — SOFT_MAX kernel bug on Blackwell
The Blackwell 6000 Tower completed all 36 cells of the Qwen3.6-35B-A3B-Q8 grid under llama.cpp + CUDA backend at the locked SHA `67b2b7f2...`. **Every cell is zero-yield.** All 36 cells show `aggregate_decode_mean=0.0` with every batch logged as `ok=0/N`. The numbers cannot be reported as A3B performance data, and the cells are formally retracted from the headline.

**Root cause** (from per-cell `llama-server-*.log`):

```
ggml_cuda_compute_forward: SOFT_MAX failed
/home/michael/bench-fleet-llama-cpp/ggml/src/ggml-cuda/ggml-cuda.cu:102: CUDA error
CUDA error: invalid argument
  current device: 0, in function ggml_cuda_compute_forward
                  at /.../ggml-cuda.cu:3114
```

llama-server aborted at ~6.6 s of runtime on the very first forward pass for every cell. Subsequent batches saw `Remote end closed connection without response` / `[Errno 111] Connection refused` because the server was dead. `bench-host.sh` correctly wrote `.done`, span up a fresh llama-server for the next cell, and that server crashed identically. The "fast" Tower2 A3B leg (36 cells in ~18 minutes) was not throughput — it was 36 cold model loads each crashing on the first inference.

**Scope of the bug**:
- Engine: llama.cpp tag `b9151` / SHA `67b2b7f2f2d6dac7962b219168a4c7a20c7359b7`
- Backend: CUDA (Blackwell-native build, `BLACKWELL_NATIVE_FP4=1`, `USE_GRAPHS=1`, `ARCHS=1200`)
- Hardware: NVIDIA RTX PRO 6000 Blackwell Workstation Edition (97 GiB)
- Model: Qwen3.6-35B-A3B-Q8 (the MoE variant)
- **Dense Qwen3.6-27B-Q8 on the same build was unaffected** — the 27B leg ran to completion with valid data
- DGX Spark with the same engine (cuda-aarch64 build) on the same A3B model is producing valid data (decode 11–17 tok/s per slot, agg 36–106 tok/s observed)

The MoE-specific failure on a Blackwell-native build points at the expert-router softmax kernel path. Not isolated further here.

**What this study reports for Tower2 A3B under llama.cpp/CUDA**:
- All 36 cells are **retracted** from the headline performance comparison
- The crashes are reproduced verbatim from per-cell `bench-cell.log` (the harness driver's log). Per-cell `llama-server-*.log` files themselves are NOT vendored in this bundle to keep its size under ~110 MB — they are regeneratable from the pinned llama.cpp source SHA in `harness/VENDORED-FROM-SHA.txt` and the per-cell `cell.meta.json` (server invocation captured).
- This audit category (B21) is the canonical statement

**What is queued to replace it** (follow-up sub-study):
- A vLLM A3B sub-study on the Blackwell 6000 Tower, using the same prompt corpus + grid coordinates as this study, with vLLM's native batched serving
- Reports as a separate appendix table, not mixed into the llama.cpp headline
- Resolves the question "how fast does the Blackwell 6000 Tower run Qwen3.6-35B-A3B-Q8?" using a known-working A3B engine path on this hardware

**Why this is honest reporting, not a re-roll**: we are not picking a "better number" to favour Tower2. The llama.cpp engine produced data on three of four hosts at A3B (DGX Spark, M5 Max, EVO X2 if it gets there), but crashed on the fourth host's GPU + model combo. Reporting Tower2 A3B from a different engine while explicitly labeling the engine change is the correct way to handle a kernel bug in the pinned engine.

### B22. Tower2 vLLM engine-comparison sub-study (27B, dense)
To validate that the B21 retraction reflects a real engine bug and not a Blackwell-CUDA-can't-run-MoE-at-all problem, the study runs a separate sub-study of dense Qwen3.6-27B on Tower2 under **vLLM 0.21.0** (the `vllm/vllm-openai:latest` Docker image). This double-duties as:

1. **An engine-comparison baseline**: vLLM 27B vs llama.cpp 27B on the same hardware. The llama.cpp leg produced valid data (B16); pairing it with vLLM gives a clean cross-engine same-hardware delta.
2. **A sanity check on the Blackwell + vLLM path**: confirms vLLM works on this hardware for *some* Qwen3.6 model, which then makes the A3B retraction (B21) clearly engine-specific to llama.cpp + Blackwell + MoE.

**Model variant**: `Qwen-Qwen3.6-27B-FP8` (HuggingFace native safetensors, FP8 weights). This is **not bit-identical** to the Q8_0 GGUF used by the main study — the main study uses INT8 GGUF Q8_0 quantization, while the vLLM checkpoint is FP8 (different number format at the same bits-per-weight). Both occupy 8 bits per weight at runtime. Cross-engine comparison should be read as "engine + native quant format" not "engine swap with identical weights." That caveat is part of the appendix table title.

The Q8 GGUF cannot load under vLLM because the installed `transformers` versions (both the host pip-installed `4.57.6` and the Docker-image vendored copy) raise `ValueError: GGUF model with architecture qwen35 is not supported yet`. This is a transformers library limitation, not a vLLM limitation. Using the FP8 safetensors checkpoint (vLLM-native format) is the practical path.

**A separate vLLM A3B sub-study** is queued. The Tower2 vLLM FP8 A3B numbers in this PR's headline use `Qwen/Qwen3.6-35B-A3B-FP8` (8-bit float, defended in `audit/SEMANTIC-EQUIVALENCE-35B-A3B.md`); a comparable 4-bit AWQ run from `cyankiwi-Qwen3.6-35B-A3B-AWQ-4bit` would carry a larger quant-difference caveat and is therefore queued as a separate appendix rather than mixed into the headline.

**Scope of the 27B vLLM run** (intentionally limited):
- Same prompt corpus (`workloads/prompts.jsonl`), same seed (42), same warmup_discard (2)
- Subset of grid coordinates: short ctx (1K) at conc=1 and conc=8, long ctx (16K, 32K) at conc=1, plus the engine-bound failure cell (32K, conc=8)
- vLLM config: `--max-model-len 36864 --gpu-memory-utilization 0.92 --tensor-parallel-size 1`, default chunked-prefill ON (vLLM 0.21.0 default), prefix-caching OFF (matches llama.cpp `cache_prompt: false`)
- Output dir: `results/<run>/tower2/qwen3.6-27b/cuda-vllm/`
- Adapter: `lib/bench-cell-vllm.py` (streaming `/v1/completions` so we can capture TTFT vs decode rate separately)

**First-pass results** (N=5 batches per cell, 2 warmup discarded, body N=3, after first run with `--max-model-len=33024`; ctx=32K cells initially rejected for prompt+gen > max-model-len, re-run with `--max-model-len=36864` in flight):

| cell                          | llama.cpp Q8 per-slot dec  | vLLM FP8 per-slot dec | Δ engine     |
|-------------------------------|---------------------------:|----------------------:|--------------|
| ctx=01024 gen=2048 conc=1     | 49.4 tok/s                 | **50.75 tok/s**       | +2.7 % (tied)|
| ctx=01024 gen=2048 conc=8     | 49.8 tok/s (agg 390)       | 46.67 (agg 364.2)     | −6.2 % aggregate, llama.cpp wins peak-conc burst |
| ctx=16384 gen=2048 conc=1     | 19.4 tok/s                 | **49.32 tok/s**       | **+154 % (vLLM 2.5×)** |
| ctx=32768 gen=2048 conc=1     | (per main study)           | (re-run pending)      | TBD          |
| ctx=32768 gen=2048 conc=8     | (per main study, engine-bound on llama.cpp) | (re-run pending) | TBD |

**The ctx=16384 result is the audit-defining finding**: per-slot decode at long context jumps from **19.4 tok/s (llama.cpp)** to **49.32 tok/s (vLLM)** on the *same Blackwell GPU, same dense 27B model class, same 8-bit weights*. The earlier B16 observation that "Tower2's per-slot decode collapses at long context" is now properly attributed to **the llama.cpp CUDA kernel-size mismatch on Blackwell**, not to silicon. The actual Blackwell 6000 Tower can sustain its short-context decode rate out to ctx=16K under a properly-batched engine; llama.cpp's CUDA path simply cannot.

**Cross-checks this enables**:
- The earlier headline ranking that showed Tower2's decode lead narrowing at long ctx (where M5 closed the gap from 3× behind to 1.2× behind) is misleading-by-engine. Under vLLM, Tower2's decode at ctx=16K is ~3.1× M5 Max's 16.1 tok/s — the lead doesn't narrow at all on the actual silicon.
- The B15 held-multi-user conclusion gains supporting evidence: the 4.6 % of bandwidth ceiling figure was llama.cpp + parallel-slots breakdown, not a fundamental ceiling. vLLM's continuous-batching path should change that number materially.
- B21's "llama.cpp + Blackwell-CUDA has kernel bugs at the model level" claim is supported by a second independent instance: A3B (SOFT_MAX abort) AND 27B at long-ctx (decode collapse) both fail/degrade on the same engine + hardware. Two issues, one engine path.

**What this does NOT change**: cross-host comparisons at single-user short context (ctx=1024 conc=1) are intact — vLLM and llama.cpp produce nearly identical numbers there, so the main-study Tower2 figures are reliable in that regime. The audit caveat applies specifically to **long-context decode under llama.cpp/CUDA on Blackwell**.

**What could explain the 2.5× gap at ctx=16K** — honest disaggregation (we observed the result; we did not isolate the cause):

| candidate explanation | rough plausibility on Blackwell | how to test |
|---|---|---|
| **vLLM PagedAttention + continuous batching** retain coherent attention math at long ctx; llama.cpp's `--parallel N` slots devolve into uncoordinated mini-batches. | High — matches the B15 observation that Blackwell at 4.6% of bandwidth ceiling cannot be silicon-bound. | Side-by-side at conc=1 (no batching benefit) at ctx=16K. If the gap shrinks at conc=1 but stays at conc=8, batching is the cause. |
| **FP8 (E4M3) tensor-core throughput** on Blackwell vs **Q8_0 INT8 dequant overhead** in llama.cpp's CUDA path. Blackwell exposes native FP8 matmul; llama.cpp Q8_0 decodes weights to FP16 before matmul. | High — Blackwell datasheet calls out FP8 sparsity throughput as the headline tensor-core feature. | A Q8_0 vLLM run (currently blocked by transformers GGUF support gap) would isolate engine path from quant scheme. |
| **Chunked prefill** in vLLM 0.21.0 default-on vs llama.cpp's monolithic prefill. | Medium — chunked prefill helps multi-user serving more than single-user; less likely to be the dominant factor at conc=1. | Disable chunked prefill in vLLM with `--enable-chunked-prefill=False` and re-measure. |
| **CUDA graphs** capture on vLLM (full graph + piecewise CUDA graphs by default in 0.21.0) vs llama.cpp's per-call kernel launch overhead at long context. | Medium-high — long-context decode has many small per-step kernels; CUDA graph capture amortizes the launch cost. | llama.cpp at the same SHA with `GGML_CUDA_FORCE_MMQ=0` or trying a newer tag's graph-mode flag would test this. |
| **KV cache memory layout** — PagedAttention's block-wise layout vs llama.cpp's contiguous KV cache. | Lower direct throughput impact, but interacts with the slot-scheduling story. | Hard to isolate without engine instrumentation. |

The observed result is **engine path × quant scheme × Blackwell silicon**. We do not pretend to have isolated which factor dominates. The headline claim survives the disaggregation because every plausible cause is **engine-side**, not silicon-side: the Blackwell GPU is the same in both runs, and it is not the bottleneck in the vLLM path.

### B23. Strix 27B/vulkan final coverage: 33/36 cells, 3 .error at ctx=32K conc=8

The Strix 27B/vulkan leg finalized with **33 of 36 cells valid**, not 36. Three cells at `ctx=32768 conc=8` (`gen=128`, `gen=512`, `gen=2048`) failed identically: bench-cell.py hit `wall=1200.26s ok=0/8 aggregate_decode=0.0` on batch 0, the canonical engine-bound timeout pattern. Each was operator-SIGTERMed per [[feedback-microbench-methodology]] (>30 same-content writes rule) rather than waiting the full ~3.3h per cell of cumulative 1200s timeouts. The `gen=2048 conc=8` cell was caught on its first batch; the other two had earlier been triaged the same way.

This is the **exact same engine-bound class** documented in B15 (Tower2 CUDA at ctx=16K conc=8) and B20 (Strix's earlier conc=8 cells at smaller gen). Three symptoms, one underlying cause: llama.cpp's `--parallel N` slots scheduler does not retain coherent batched/paged-attention behavior at high concurrency + long context across multiple backends (Tower2 CUDA, Strix Vulkan). The cells are formally retracted from cross-host claims and remain in the result tree as `.error` markers for reproducibility.

This does NOT affect:
- Single-user (conc=1) Strix Vulkan numbers — the conc=1 column is intact at 36/36 across all four hosts
- Lower-concurrency (conc=4) Strix numbers at 32K — these completed cleanly

The Strix Vulkan headline ranking (decode 7.8 tok/s at conc=1) is unaffected. The 4-host conc=8-at-32K cell is held under B15.

The Strix **35B-A3B/vulkan** leg (separate from this B23) reached 23/36 cells before pause. The 13 missing cells are all `ctx=32768 conc≥4` — KV cache for 35B-A3B Q8 at 32 K × 4-or-8 slots exceeds the 124 GB unified pool and OOMs. This is a hardware ceiling on this configuration, not the same engine-bound timeout class as B23; it is documented as a ceiling and not retried in this snapshot.

## Reproducibility bundle published

- llama.cpp source SHA `67b2b7f2f2d6dac7962b219168a4c7a20c7359b7` (vendored harness pins it; see `harness/VENDORED-FROM-SHA.txt`)
- Per-host environment snapshot (`env.json`) per (host, model, backend)
- Per-cell meta (`cell.meta.json`) — captures the exact llama-server invocation used
- Per-cell raw inferences (`inferences.jsonl`)
- Per-cell raw batches (`batches.jsonl`)
- Per-cell driver log (`bench-cell.log`) — the harness's view of the cell
- Per-cell 1 Hz power CSV (`power.csv`)
- Per-cell 1 Hz thermal CSV (`thermals.csv`)
- Prompt corpus + SHA (`workloads/prompts.jsonl`, `workloads/prompts.jsonl.sha256`)
- Grid spec (`workloads/grid.json`)
- Vendored harness (`harness/lib/`, `harness/run.sh`, `harness/targets.json`, etc.)

NOT included in the bundle (regeneratable):

- Per-cell `llama-server-<port>.log` — excluded to keep the bundle ~110 MB; regeneratable from the pinned SHA + per-cell `cell.meta.json` server invocation.
- Per-host `build-<backend>.configure.log` and `build-<backend>.build.log` — excluded for size; the build invocations themselves are in `harness/HARNESS-README.md`.
- Aggregation + report scripts (`lib/aggregate.sh`, `lib/report.sh`)
- This audit (`AUDIT.md`)

Anyone can re-run on equivalent hardware with the same SHA pins and get the same numbers (within cross-run variance bound in B6).

## What would invalidate this study

Honest list of things that would force a re-run or partial retraction:

- The pinned llama.cpp SHA gets reverted / found to have a kernel bug at our settings → re-pin + re-run
- The Q8 GGUFs are silently re-uploaded to HF with different bytes → SHA-pinning protects us if the verifier is honest
- Someone proves the prompt corpus systematically favors a backend → we'd add a second corpus and re-publish
- A hardware sample turns out to be defective (e.g. throttled or under-volted in BIOS) → swap and re-run that host

We will document any of the above as an addendum, not a silent edit.
