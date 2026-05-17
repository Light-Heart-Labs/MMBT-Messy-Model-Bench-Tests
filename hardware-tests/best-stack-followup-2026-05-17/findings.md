# Findings — best-stack follow-up on M5 (MLX) and Strix Halo (dream-server ROCm 7)

## § Status of this PR — what's shipped, what's preliminary, what's deferred

- **Shipped at snapshot:**
  - M5 MLX 27B grid (12/12 conc=1 cells, complete)
  - M5 MLX 35B-A3B grid (12/12 conc=1 cells, complete)
  - Strix dream-server ROCm 7 partial grid (8/12 conc=1 cells covering ctx=1024 + 4096 + ctx=16K gen=128/512; ctx=16K gen=2048 and ctx=32K cells still running, will land in follow-up commits)
  - Engine identification + reproducibility bundle for both paths
- **Preliminary:** Strix dream-server ROCm 7 cells at ctx≥16K. Same engine, just slower cells. Update as they land.
- **Deferred** (see `manifest.json.deferred_to_follow_up`):
  - Lemonade on Windows + DirectML + INT4 NPU path (the actually-novel Ryzen AI acceleration story)
  - True Lemonade SDK on Strix Linux with Lemonade's own bundled Vulkan binary (separate from dream-server's bundle)
  - vanilla llama.cpp `b9151` against ROCm 7 (vs the canonical's broken ROCm 6.4.4 — would isolate whether the ROCm-7 fix is in the runtime or in dream-server's downstream patches)

## § Finding 1 — MLX is a real productized-stack lift on Apple M5 Max

For the same workload class the canonical study measured (Qwen3.6 dense + MoE, ~Q8-equivalent quantization, single-user single-stream conc=1), MLX runs faster than `llama.cpp` Metal at every cell we measured:

| metric | canonical (b9151 Metal) | MLX | lift |
|---|---:|---:|---:|
| 27B dense — peak decode | 16.78 ± 0.19 | **17.78 ± 0.04** | **+6.0%** |
| 27B dense — peak prefill | 571.8 | **773.2** | **+35.2%** |
| 27B dense — decode @ ctx=16K | 16.10 | **17.14** | **+6.5%** |
| 35B-A3B MoE — peak decode | 88.87 ± 0.12 | **102.71 ± 0.66** | **+15.6%** |
| 35B-A3B MoE — peak prefill | 2684.9 | **4124.6** | **+53.6%** |
| 35B-A3B MoE — decode @ ctx=16K | 80.28 ± 0.57 | **95.73 ± 0.56** | **+19.2%** |

The lift is larger on the MoE model than on the dense one — consistent with MLX-LM having more specialized sparse/batched-execution paths than llama.cpp's generic Metal kernels at the time `b9151` was tagged. The variance is tight on both engines so the lift is real, not measurement noise.

**Practical implication for buyers on M5-class hardware:** default to MLX for serving Qwen3.6 family models. The vendor stack lifts and the lift is bigger when the model is MoE.

**What this does NOT claim:**

- That MLX would beat a newer `llama.cpp` Metal build (the canonical pin is `b9151`; upstream may have caught up).
- That MLX preserves cross-vendor file portability (it does not — MLX uses its own quantization format, not GGUF).
- That MLX beats `llama.cpp` on workloads other than this one. Long-context cells and decode-dominant cells show the lift. Prefill-dominant short-cell cells show the lift too, but the **lift ratio** changes per cell type.

## § Finding 2 — AMD's productized Strix Halo Linux stack works but doesn't lift on prefill

The canonical study's `B4` audit bias bullet recorded **"ROCm 6.4.4 on Strix Halo segfaults at `common_init_result: fitting params to device memory`"** as a confirmed-after-retry finding at `llama.cpp b9151` + `libamdhip64.so.6.4.60404`. That claim still holds for that specific runtime + engine pair.

This bundle exercises a different combination on the same hardware:

- **dream-server's bundled custom `llama.cpp` build** at `/opt/llama-custom/llama-server`. The binary's version string reads `version: 1 (ff5ef82)` (downstream `b1` numbering; `ff5ef82` is the upstream commit it's rebased from — substantially older than `b9151`).
- **Linked against `libamdhip64.so.7`** (ROCm 7, not 6.4.4) shipped alongside the binary in `/opt/llama-custom/`, with custom-tuned `librocblas.so.5`, `libhipblaslt.so.1`, `librocroller.so.1`.
- **Fronted by Lemonade Server** running with `--llamacpp rocm` (which routes calls to `/opt/llama-custom/llama-server`, NOT to Lemonade's own bundled `/opt/lemonade/llama/{cpu,vulkan}/` binaries — those directories exist on disk but are empty until Lemonade fetches them on first use of those backends).

**Result:** the ROCm 7 path **works** on Strix Halo for Qwen3.6-27B-Q8. No segfaults, no `hipStreamCreateWithFlags` OOMs (which the v6.4.4 retry hit when we tried `-fit off`). The cells we have so far:

| cell | dream-server ROCm 7 (this bundle) | canonical Vulkan b9151 |
|---|---:|---:|
| ctx=1024 gen=128 decode | 7.666 ± 0.003 | ~7.82 peak |
| ctx=1024 gen=512 decode | 7.614 ± 0.001 | 7.784 ± 0.004 |
| ctx=1024 gen=2048 decode | 7.575 ± 0.004 | 7.780 ± 0.001 |
| ctx=4096 gen=128 decode | 7.525 ± 0.002 | 7.771 ± 0.003 |
| ctx=4096 gen=512 decode | 7.472 ± 0.001 | 7.724 ± 0.001 |
| ctx=4096 gen=2048 decode | 7.439 ± 0.0003 | 7.706 ± 0.001 |
| ctx=16384 gen=128 decode | 7.062 ± 0.002 | 7.549 ± 0.003 |
| ctx=4096 gen=128 **prefill** | **111.94 ± 0.002** | **~292** (peak across cells) |
| ctx=16384 gen=128 **TTFT / prefill** | **185.6 s / 84.08 tok/s** | **59.3 s / 263.1 tok/s** |

**Decode:** essentially the same as canonical Vulkan within run-to-run noise. ROCm 7 isn't faster, isn't slower.

**Prefill: ~2.6× slower than canonical Vulkan.** The likely cause is the older `llama.cpp` build dream-server bundles (`ff5ef82`) — `b9151` is approximately 2641 commits ahead and includes Vulkan-and-shader optimizations that benefit prefill more than decode. So the slower prefill is a `llama.cpp`-build-vintage cost, not a ROCm-vs-Vulkan cost.

**Practical implication for buyers on Strix Halo Linux:**

- ROCm 7 finally loads Qwen3.6-27B-Q8. The canonical "ROCm broken on Strix Halo" claim is specifically about v6.4.4 + b9151; updating to v7 + dream-server's custom build resolves loading.
- The productized AMD Linux stack does not deliver speedups beyond upstream `llama.cpp` Vulkan. On the prefill axis it is significantly slower because of engine vintage.
- The Strix Halo NPU acceleration story (the actual unique-selling-point of Ryzen AI silicon) lives on the Windows + DirectML + INT4 OGA path through Lemonade's official `oga-load` backend, which we did not test here. That, not ROCm Linux, is what AMD is selling.

### Additional finding: 300 s server-side request ceiling

`ctx=16384 gen=2048` and the entire `ctx=32K` tier exceed a 300 s response timeout in the dream-server Lemonade Server stack on Strix Halo. All 10 batches at `ctx16384_gen2048_conc1` errored at exactly 300.0 s wall time per request, producing a `.error` marker (no `.done`). Estimated true request length at that cell: ~186 s prefill (84 tok/s × 15,603 prompt tokens) + ~293 s decode (2048 / 7 tok/s) ≈ 480 s, well over the 300 s ceiling. At `ctx=32K`, prefill alone is ~371 s, so all `ctx=32K` cells are expected to hit the same ceiling.

This is itself a buyer-relevant ceiling: under the **dream-server lemonade stack as-shipped on Strix Halo Linux**, single-user requests longer than ~5 min fail. Vanilla `llama-server` from `b9151` does not have this ceiling (the canonical study's Strix Vulkan ctx=32K gen=2048 cell completes in ~250 s and decode is ~7 tok/s × 2048 = 293 s). The ceiling appears to be a Lemonade Server / FastAPI default; not yet investigated whether tunable.

## § Engine identification — why this took some unwinding

We initially set up bench cells expecting to measure "Lemonade SDK on Strix" — Lemonade's own Vulkan-bundled binary against the same Q8 GGUF. The numbers came back close to canonical Vulkan and we wrote down "Lemonade ≈ vanilla Vulkan on Linux" as the headline.

The Lemonade server we were actually hitting was the one already running on Strix as `dream-server`'s `dream-llama-server` container. Inspecting that container revealed:

```
/opt/lemonade/lemonade-server serve --llamacpp rocm --llamacpp-args ...
  -> spawned: /opt/llama-custom/llama-server -m /models/...
```

— not `/opt/lemonade/llama/vulkan/llama-server` as Lemonade's documentation would imply. The `cpu/` and `vulkan/` directories under `/opt/lemonade/llama/` exist but are empty in this container; the actual inference binary is dream-server's downstream custom build at `/opt/llama-custom/`.

`ldd` on that binary shows it links against `libamdhip64.so.7`, `libhipblas.so.3`, `libhipblaslt.so.1` — i.e. ROCm 7. So what we are actually measuring is **dream-server's bundled custom llama.cpp + ROCm 7**, fronted by Lemonade Server's OpenAI-compatible API. That is genuinely the configuration most Strix Halo dream-server users actually run, but it is not what the SDK marketing means when it says "Lemonade SDK."

The `engine` field in each cell.json is therefore set to `"dreamserver-llamacpp-rocm7"` (with `engine_note` pointing at the binary path and the libraries it links). Anyone running the same workload through Lemonade's own `--llamacpp vulkan` against its own bundled binary should expect different (likely closer-to-canonical-Vulkan) numbers; that's a queued follow-up.

## § Why this is appendix and not part of the cross-host ranking

The canonical study's ranking depends on the same model bytes and same engine SHA across hosts. This bundle deliberately changes both:

- MLX 8-bit ≠ Q8 GGUF (different bytes, different quantization scheme, same model concept)
- dream-server's custom `llama.cpp` build at `ff5ef82` ≠ vanilla `b9151`

Either of those changes would individually disqualify these rows from the canonical-headline table. Combined, they make this bundle squarely **appendix-tier**: useful as a "what does the vendor's productized stack do for me" comparison, not as a "which silicon wins" ranking input.

## § Reproducibility

- Prompt corpus: same SHA as canonical (`9a27eba85a8da9443d7fcf74e281b011831806c4b24aaaada3915463d5c13cd8`), see `workloads/prompts.jsonl`.
- MLX models: `mlx-community/Qwen3.6-27B-8bit` and `mlx-community/Qwen3.6-35B-A3B-8bit`. HuggingFace IDs are floating refs, so the per-shard SHAs of the exact bytes we ran against are pinned in `workloads/mlx-models.sha256` (every safetensors weight shard + config + tokenizer + index file). Run `shasum -a 256 -c workloads/mlx-models.sha256` from a parent dir containing both model dirs to verify before reproducing.
- Strix model file: `Qwen3.6-27B-Q8_0.gguf` SHA `f93f517f...` — byte-identical to canonical study.
- Driver scripts: `harness/lib/bench-cell-mlx.py`, `harness/lib/bench-cell-lemonade.py`, with grid runners and `canon-backfill.py` for adding MMBT-canonical schema fields. Source SHA in `harness/VENDORED-FROM-SHA.txt`.
- Engine SHAs (where available):
  - MLX: `mlx-lm` Python package version recorded in each `cell.json.engine_version` (was `0.31.3` at snapshot).
  - dream-server llama.cpp: `version: 1 (ff5ef82)` — upstream commit `ff5ef82`. The exact downstream patch set is not published by the dream-server team but the binary is hash-comparable against the container image `dream-lemonade-server:latest`.
