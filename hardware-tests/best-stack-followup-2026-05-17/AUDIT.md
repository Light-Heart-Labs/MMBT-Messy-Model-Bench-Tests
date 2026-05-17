# AUDIT — best-stack follow-up bundle (2026-05-17)

This bundle deliberately changes engines from the canonical [`qwen3.6-q8-fleet-2026-05-17`](../qwen3.6-q8-fleet-2026-05-17/) study to answer a specific vendor-stack question (does the productized stack accelerate the workload?). That makes the apples-to-apples boundary subtler than the canonical study's, so this audit doc walks through what's locked, what varies, and what the comparison can and cannot support.

## What is locked across the canonical study and this bundle

- **Prompt corpus**: byte-identical to canonical. SHA-pinned (`9a27eba85a8da9443d7fcf74e281b011831806c4b24aaaada3915463d5c13cd8`); verifiable via `workloads/prompts.jsonl.sha256`. The same 120 prompts at four context targets were sent to every host in both studies.
- **Generation parameters**: temperature=0, seed=42, max_tokens fixed per cell, `cache_prompt=false` for the Lemonade/dream-server runs (no warm-cache short-circuit) to match the canonical study's no-cache discipline.
- **Grid**: 4 ctx × 3 gen lengths × N=10 (2 warmup discarded) per cell. Same shape as the canonical conc=1 column.
- **Hosts**: physical machines are the same. M5 Max MBP (same chassis, same SoC, same room), EVO X2 / Strix Halo (same chassis, same SoC, same room).
- **Scope statement**: single-user (conc=1) only, exactly as in the canonical study's headline. Multi-user (conc≥4) is out of scope on purpose.

## What varies (the whole point of this bundle)

| axis | canonical | this bundle | why varied |
|---|---|---|---|
| Engine, M5 side | llama.cpp Metal at SHA `67b2b7f2f` (`b9151`) | Apple `mlx-lm` 0.31.3 Python API | Tests whether Apple's productized stack lifts. |
| Engine, Strix side | llama.cpp Vulkan at SHA `67b2b7f2f` (`b9151`) | dream-server bundled custom llama.cpp build at upstream commit `ff5ef82`, linked against ROCm 7 (`libamdhip64.so.7`) + custom `librocblas`/`libhipblaslt`. Fronted by Lemonade Server's OpenAI-compatible API. | Tests AMD's productized stack on Strix Halo. ROCm 7 (a newer runtime than the canonical's failing 6.4.4) is what dream-server ships in production. |
| Model bytes, M5 side | `Qwen3.6-27B-Q8_0.gguf` and `Qwen3.6-35B-A3B-Q8_0.gguf` (GGUF Q8_0) | `mlx-community/Qwen3.6-27B-8bit` and `mlx-community/Qwen3.6-35B-A3B-8bit` (MLX-native 8-bit) | MLX uses its own quantization format; same model concept, different bytes. SHA-pinned per shard in `workloads/mlx-models.sha256`. |
| Model bytes, Strix side | `Qwen3.6-27B-Q8_0.gguf` SHA `f93f517f…` | Same file, byte-identical | The GGUF path is one of the two factors that lets the Strix vs canonical comparison stay meaningful on file content. |
| Concurrency wrapper | `bench-cell.py` hitting llama-server `/completion` | `bench-cell-mlx.py` calling `mlx_lm.stream_generate` directly OR `bench-cell-lemonade.py` hitting Lemonade `/v1/completions`. | Different APIs. Schemas converge via `harness/lib/canon-backfill.py` so cell.json fields match canonical. |

## Apples-to-apples boundaries (what the comparison can and cannot support)

This bundle **can** support claims about:

- **MLX vs llama.cpp Metal** on the SAME M5 hardware for Qwen3.6 dense + MoE at ~8-bit quantization, single user. Decode and prefill numbers are directly comparable in tok/s, and the model is the same model concept at the same nominal precision.
- **dream-server ROCm 7 vs llama.cpp Vulkan b9151** on the SAME Strix Halo hardware for Qwen3.6-27B-Q8 GGUF (byte-identical file), single user. Decode is comparable directly; prefill cost can be attributed to engine vintage because the bundled custom llama.cpp build is older than canonical's pin.
- **ROCm 7 loads where ROCm 6.4.4 did not** for the canonical workload on Strix Halo. This narrows (does not invalidate) the canonical "ROCm broken" claim — see `[hw.best-stack.strix-halo.rocm7-works]` in `claims.yaml`.

This bundle **cannot** support claims about:

- **Cross-host ranking.** The canonical study owns that and this bundle does not feed it.
- **Engine quality / output correctness differences.** Outputs are deterministic at temperature=0 / seed=42, but MLX uses a different quantization scheme than GGUF Q8. We do not run a semantic-equivalence diff between MLX 8-bit and GGUF Q8 outputs in this bundle (could be a follow-up).
- **NVIDIA productized stack** (vLLM / TensorRT-LLM / SGLang on Tower2). Canonical study's vLLM Tower2 row is the existing data point; not re-covered here.
- **Multi-user serving.** conc≥4 is held in canonical and held here.
- **Lemonade SDK's own bundled Vulkan binary.** We caught during bring-up that the Lemonade Server we were hitting (the one running in dream-server's `dream-llama-server` container) is fronting dream-server's custom `/opt/llama-custom/` binary, NOT Lemonade's own `/opt/lemonade/llama/vulkan/` binary (those dirs exist but are empty in this container; Lemonade's own binaries only get fetched on first use of those backends). To test pure Lemonade-Vulkan against the same model we would need to spin up a separate Lemonade Server with `--llamacpp vulkan` and let it download its own binary; that is a queued follow-up.
- **Strix Halo NPU acceleration.** The actually-novel Ryzen AI productized path is the Lemonade `oga-load` backend on Windows + DirectML + INT4 OGA models. We do not have a Windows Strix Halo host; that path is not exercised here.

## Specific biases (this study's B-list, complementing canonical's)

### BA1. Engine vintage cost on the Strix dream-server side
dream-server bundles llama.cpp at upstream commit `ff5ef82`. Canonical pin is `67b2b7f2` (`b9151`), which is approximately 2641 commits ahead. Many of the Vulkan-and-shader optimizations between those commits land in the prefill path. The canonical Vulkan prefill of 292.3 tok/s at the peak cell vs this bundle's 120 tok/s is therefore an engine-vintage delta primarily, not a ROCm-vs-Vulkan delta. The decode-rate equivalence (within noise) suggests the decode path is similarly optimized in both versions or is bandwidth-limited rather than kernel-limited on this hardware.

### BA2. MLX quant scheme is not GGUF Q8
`mlx-community/Qwen3.6-27B-8bit` is MLX's own 8-bit affine quantization, applied at MLX-format conversion time. GGUF `Q8_0` is llama.cpp's 8-bit quantization. Both are "8 bits per weight" at coarse granularity but the layouts, scale factors, and per-group bookkeeping differ. So a same-precision-different-bytes story. Quality is not measured in this bundle.

### BA3. MLX concurrency semantics differ
`bench-cell-mlx.py` runs concurrent slots **sequentially** within a batch (not asyncio-parallel), unlike `bench-cell.py`'s `asyncio.gather` against llama-server's `--parallel N` slots. This bundle reports `conc=1` only, so the difference is moot — but if a future commit adds `conc≥4` to MLX cells, the data must be tagged differently because the throughput semantics are NOT comparable to canonical's slot-parallel numbers.

### BA4. `cache_prompt` flag handling between engines
We verified empirically that `cache_prompt=false` in the request body is honored by the Lemonade-fronted dream-server llama.cpp binary (the body field passes through). The MLX driver creates a fresh KV cache per `stream_generate` call by construction so `cache_prompt` is not applicable. Both paths therefore do a full prefill per inference, matching the canonical study's discipline.

### BA5. Power / thermals not co-sampled
Canonical study has 1 Hz power + thermals CSVs per cell. This bundle does NOT — we wanted to ship the productized-stack-comparison data quickly. The thermal-class story from canonical (`hw.q8.chassis-thermal-class`) still applies to the same chassis under similar workload intensities; we do not re-measure.

### BA6. Cold-start exposure differs per engine
- MLX `bench-cell-mlx.py` records `cold_start.decode_tps` from batch 0's first stream tick. Model load time is reported separately as `load_time_s`.
- dream-server's Lemonade-fronted llama.cpp warms the model at `/api/v1/load` time (not at first `/v1/completions`); our `cold_start` for those cells therefore reflects "first request after API-level model load", not "first request after process start". Different from canonical's bench-host warmup; comparable across cells *within* this bundle.

### BA7. Engine identification was nontrivial; future readers should not trust the `engine` field blindly
We initially labeled the Strix cells `lemonade-llamacpp-vulkan` because the Lemonade Server CLI exposed `--llamacpp {vulkan,rocm,cpu}` and we assumed the productized SDK shipped the same Vulkan binary we expected. Inspecting the container's running process revealed it was actually `/opt/llama-custom/llama-server` (dream-server's downstream custom build) with `libamdhip64.so.7` (ROCm 7) linked. We relabeled to `dreamserver-llamacpp-rocm7` and added `engine_note` fields pointing at the binary path + library set. Future reviewers running similar bundles should always `ldd` the actual inference binary.

### BA8. HF refs are floating; weight bytes are pinned only by `mlx-models.sha256`
The README's `hf download mlx-community/Qwen3.6-27B-8bit` command will pull whichever revision Hugging Face serves at the time. The actual bytes we ran against are captured in `workloads/mlx-models.sha256`. Reviewers verifying decode/prefill numbers should `shasum -c` against that file before quoting our deltas — if HF rev moves the weights underneath, our numbers might not reproduce on a fresh pull.

## Reproduction checklist

1. `shasum -a 256 -c workloads/prompts.jsonl.sha256` → prompt corpus byte-identical to canonical.
2. `cd ~/models/mlx && shasum -a 256 -c <bundle>/workloads/mlx-models.sha256` → MLX weight shards byte-identical to ours.
3. `sha256sum Qwen3.6-27B-Q8_0.gguf` → `f93f517f38e696d35a1a7df2c0e3155a64f4c4dcd662107a146ae263f7fb14ce` (the canonical study's pin; same file for Strix side here).
4. MLX engine: `pip install mlx-lm==0.31.3` (or `>=0.31.3`; record version in `cell.json.engine_version`).
5. dream-server engine: clone `dream-lemonade-server:latest` container; binary at `/opt/llama-custom/llama-server`. `ldd` should show `libamdhip64.so.7`.
6. Run `harness/lib/run-mlx-grid.sh` on M5 and `harness/lib/run-lemonade-grid.sh` on Strix.
7. Verify `aggregate/headline.csv` recomputes via `python3 harness/lib/build-headline.py --bundle . --out /tmp/check.csv && diff aggregate/headline.csv /tmp/check.csv`.
