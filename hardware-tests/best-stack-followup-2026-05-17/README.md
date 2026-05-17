# Best-stack follow-up — MLX on M5, dream-server ROCm 7 on Strix — 2026-05-17

This bundle answers the [`qwen3.6-q8-fleet-2026-05-17`](../qwen3.6-q8-fleet-2026-05-17/) audit's "best-stack matrix" gap for Apple and AMD: what happens when each vendor's productized inference stack runs against the same workload the canonical study ran on vanilla `llama.cpp` at the pinned `b9151` SHA?

- **Apple side:** Qwen3.6-27B and Qwen3.6-35B-A3B in their **native MLX 8-bit format** (`mlx-community/Qwen3.6-27B-8bit`, `mlx-community/Qwen3.6-35B-A3B-8bit`) via the `mlx-lm` Python API on M5 Max MacBook Pro.
- **AMD side:** Qwen3.6-27B Q8 GGUF (the same byte-identical file the canonical study used) served by **dream-server's bundled custom `llama.cpp` build** (`/opt/llama-custom/llama-server`) running on **ROCm 7** (`libamdhip64.so.7`), fronted by Lemonade Server's OpenAI-compatible API on Strix Halo.

This is **not** a re-run of the canonical study under different engines. The canonical study locks model bytes + engine SHA on purpose, and that constraint is what its claims rest on. This bundle deliberately varies the engine to answer a different question: *does the vendor's productized stack accelerate the workload beyond upstream `llama.cpp`?*

## Read order

1. **`findings.md`** — narrative, the two-vendor opposite-direction story (MLX lifts on Apple; ROCm 7 on Strix works but doesn't lift on prefill), and the dream-server stack identification that we needed to do before this could be interpreted.
2. **`AUDIT.md`** — what's locked vs varies relative to the canonical study, the engine-identification details that make these numbers meaningful, and where the comparison is and is not apples-to-apples.
3. **`aggregate/headline.csv`** — peak prefill, peak decode, decode-at-ctx-16K per (host, model, backend) for conc=1.
4. **`manifest.json`** — file inventory, status per dataset, the deferred follow-up list, the SHA pins.
5. **`<host>/<model>/<backend>/<cell>/cell.json`** — per-cell summaries in MMBT canonical schema (matches `qwen3.6-q8-fleet-2026-05-17`).

## Status of this bundle

This is an early publication while the grids are still running. **Read `findings.md § Status of this PR` before quoting any number.** The state at snapshot is:

| dataset | cells_present (conc=1) | cells_planned (conc=1) | status |
|---|---:|---:|---|
| `m5-mbp/qwen3.6-27b/mlx/` | 12 | 12 | complete |
| `m5-mbp/qwen3.6-35b-a3b/mlx/` | 12 | 12 | complete |
| `strix-halo/qwen3.6-27b/dreamserver-llamacpp-rocm7/` | 6 | 12 | preliminary (ctx≤4K cells; ctx=16K + 32K still running, will land in follow-up commit) |

Multi-user (`conc≥4`) cells are out of scope here exactly as in the canonical study; they would not change the buyer story this bundle settles.

## Headline at a glance

| host | model | backend | peak prefill tok/s | peak decode tok/s ± SD | decode @ ctx=16 K |
|---|---|---|---:|---:|---:|
| M5 Max MBP | Qwen3.6-27B | mlx | 773.2 | **17.78 ± 0.04** | 17.14 |
| M5 Max MBP | Qwen3.6-35B-A3B | mlx | **4124.6** | **102.71 ± 0.66** | 95.73 |
| EVO X2 (Strix Halo) | Qwen3.6-27B | dreamserver-rocm7 | 120.0 | 7.67 ± 0.003 | _ctx=16K cell pending_ |

vs the canonical-study numbers (`qwen3.6-q8-fleet-2026-05-17/aggregate/canonical-headline.csv`) for the same hardware on llama.cpp:

| host | model | canonical engine | canonical peak decode | this-bundle peak decode | lift |
|---|---|---|---:|---:|---:|
| M5 Max MBP | 27B | llama.cpp Metal (b9151) | 16.78 | **17.78** | **+6.0%** |
| M5 Max MBP | 35B-A3B | llama.cpp Metal (b9151) | 88.87 | **102.71** | **+15.6%** |
| EVO X2 | 27B | llama.cpp Vulkan (b9151) | 7.82 | 7.67 | −1.9% (within noise) |

And for prefill:

| host | model | canonical peak prefill | this-bundle peak prefill | delta |
|---|---|---:|---:|---:|
| M5 Max MBP | 27B | 571.8 | **773.2** | **+35.2%** |
| M5 Max MBP | 35B-A3B | 2684.9 | **4124.6** | **+53.6%** |
| EVO X2 | 27B | 292.3 | 120.0 | **−59.0% (older llama.cpp wrapped by dream-server)** |

## The two takeaways

1. **MLX on M5 Max is a real productized-stack lift over llama.cpp Metal.** Decode +6% on dense, +15.6% on MoE; prefill +35-54%. SDs are tight. Apple's vendor stack does what its marketing claims for this workload. Buyers on M5-class hardware should default to MLX for these models.

2. **AMD's productized stack on Linux ≈ vanilla llama.cpp Vulkan, plus an older engine cost on prefill.** dream-server ships a custom `llama.cpp` build linked against ROCm 7 (vs the canonical study's broken ROCm 6.4.4). The ROCm 7 path **works** — that resolves the canonical study's "ROCm broken on Strix Halo" claim for the v7 runtime — but its measured decode matches Vulkan within noise and its prefill is much slower because the bundled engine is at an older `llama.cpp` build than the canonical pin. Buyers on Strix Halo Linux get **no acceleration** from the productized AMD stack over upstream Vulkan; the entire claimed advantage of Lemonade/Ryzen-AI on this hardware is the Windows + DirectML + INT4 path (the actually-novel NPU acceleration), which we did not test here.

## Reproducing

```bash
# 1. Same Qwen3.6-27B Q8 GGUF file as canonical study (used by Strix run here)
sha256sum --check <<'EOF'
f93f517f38e696d35a1a7df2c0e3155a64f4c4dcd662107a146ae263f7fb14ce  Qwen3.6-27B-Q8_0.gguf
EOF

# 2. MLX models (different format from GGUF — this is the point of the comparison)
hf download mlx-community/Qwen3.6-27B-8bit     --local-dir ~/models/mlx/Qwen3.6-27B-8bit
hf download mlx-community/Qwen3.6-35B-A3B-8bit --local-dir ~/models/mlx/Qwen3.6-35B-A3B-8bit
# Verify against the byte-pinned SHAs we ran against (HF refs are floating):
cd ~/models/mlx && shasum -a 256 -c <path-to-this-bundle>/workloads/mlx-models.sha256

# 3. Same prompt corpus as canonical, SHA-pinned
cd <path-to-this-bundle> && sha256sum -c workloads/prompts.jsonl.sha256
# (or `shasum -a 256 -c workloads/prompts.jsonl.sha256` on macOS)

# 4. MLX driver (M5): see harness/lib/bench-cell-mlx.py + harness/lib/run-mlx-grid.sh
# 5. Lemonade-via-dream-server driver (Strix): see harness/lib/bench-cell-lemonade.py + harness/lib/run-lemonade-grid.sh

# Engine identifiers in cell.json:
#   "engine": "mlx"                         (also engine_version + load_time_s)
#   "engine": "dreamserver-llamacpp-rocm7"  (with engine_note pointing at binary + runtime)
```

Harness is vendored at `harness/lib/` (snapshot of `bench-fleet` at the SHA in `harness/VENDORED-FROM-SHA.txt`).

## What this bundle does NOT settle

- **Cross-host ranking.** The canonical study owns that. Different engines + different quants make this bundle appendix-only.
- **NVIDIA productized stack on Tower2.** The canonical study already shows vLLM/FP8 on Tower2; this bundle does not re-cover that ground.
- **Apple MLX on the 35B at the absolute longest cell.** Complete in this snapshot — the early-publication caveat is now closed for both MLX grids.
- **Lemonade's other backends.** We measured the path dream-server users actually run on Strix Halo Linux. The Windows + DirectML + INT4 NPU path (the actual reason to buy a Ryzen AI laptop) requires a Windows host we did not have available.
- **Multi-user (conc≥4) cells.** Out of scope here as in the canonical study.

See `manifest.json.deferred_to_follow_up` for the full list.
