# Not here yet

`KNOWN-LIMITATIONS.md` catalogs caveats on what we *did* measure. This file catalogs what we **haven't measured at all**. It exists so a reader can tell at a glance which silences are deliberate scope holdouts, and so contributors know where pull requests are most valuable.

If you're considering reproducing or extending this corpus, the bullets below are ranked roughly by how much they'd move the trustworthiness needle if filled.

## Hardware-tests gaps

### Cross-engine serving on a fixed hardware ranking

We currently run llama.cpp at one pinned SHA across four hosts, plus a small vLLM appendix on Tower2. The biggest single shift in the headline numbers will come from running the SAME models on each host under the *best practical engine* for that host:

- **NVIDIA** — vLLM 0.21+ (already started on Tower2), TensorRT-LLM, sglang.
- **Apple** — MLX with quantization choices appropriate to Apple Silicon (mlx-lm, MLX-Vision-style models).
- **AMD** — ROCm under llama.cpp (retry), vLLM with ROCm 6.4+, llama.cpp Vulkan as already covered.

The vLLM appendix on Tower2 already showed a 2.5× engine gap at ctx=16K conc=1. We expect similar engine-vs-engine gaps on the other hosts; their absence makes the cross-host ranking less defensible at long context.

### Quality companion (MMBT Phase B Q8 task-family scoring)

The published study reports performance only. We have an existing 12-task-family quality suite (`benchmarks/microbench-2026-04-28/`) at N=10; running it on both Q8 models is a separate eval that pairs with the perf data. Without it, "Q8 is fast on Tower2" is half the story; the other half is "Q8 is *good enough* on Tower2 to be useful."

### Cross-day variance

Every cell is run once. N=10 within a cell captures intra-cell variance; cross-day variance is uncharacterized. We believe it's <2 % for these workloads but haven't measured it. The fix: rerun a small set of cells on at least three different days at the same wall-clock time, on the same hardware, and characterize SD.

### Wall-AC power on every host at the same cell

Currently we have plug-meter readings on two of four hosts (M5 Max, Blackwell 6000 Tower), and only at *one* cell each. The 5-year TCO table extrapolates from those single readings. To firm it up:

- Plug-meter every host at the same standardized cell (recommend ctx=1024 conc=8 short-burst peak).
- Plug-meter on the *peak* cell of each host (where the silicon actually maxes out).
- Plug-meter under idle to characterize the always-on baseline.

The DGX Spark and EVO X2 5-yr TCO numbers in the headline cost section are *estimated*, not measured, and labeled as such.

### Cross-platform repeatability under two units per host

Every host in the published study is a sample of one. A defective unit (BIOS-throttled, under-volted, broken thermal interface) would silently bias one row. Industrial-strength would be at least two units of each platform; community-strength would be at least one independent reproducer per platform from someone else's hardware.

### Wider hardware sampling

The four hosts published are not a complete view of "local AI hardware in 2026." Notable absences:

- **RTX 5090** — same silicon family as the Blackwell 6000 Tower's PRO 6000, smaller VRAM (32 GB), much wider buyer base. Models that fit (27B Q8) should read-across within a few percent at the same power; models that don't (35B-A3B Q8 at 36.9 GB) won't fit. Both data points are interesting.
- **RTX 4090 / 3090 24 GB / RTX 6000 Ada 48 GB** — common buy points the discrete-GPU community considers vs. Apple Silicon. Without them, "Blackwell vs Apple" is one Blackwell SKU on the high end.
- **AMD W7900 / Radeon Pro / Instinct MI300X** — proper professional AMD parts vs. the Strix Halo APU we benched.
- **Mac Studio M5 Ultra / Mac Pro** — desktop-class Apple Silicon vs. the laptop we tested.
- **Other Strix Halo variants** — we tested one specific NUC-class chassis; the Strix Halo silicon will perform differently in different thermal envelopes.

### Sustained-thermal throttle curves

The published study has psychrometer field measurements at the 15.5 h mark, which IS load-bearing. The 30-min sustained-tier throttle-curve sub-study (one cell per host, sampled at 1 Hz across the duration) is currently only one cell each on three of four hosts — labeled `preliminary` in the manifest.

### Memory bandwidth sweep

The held multi-user conclusion argues that conc≥4 is engine-bound, not silicon-bound. The strongest way to confirm that empirically is a memory-bandwidth sweep with a synthetic workload that bypasses llama.cpp scheduling (e.g. raw GEMM benchmarks at the same matrix sizes the model uses internally). Doesn't replace the multi-user study; complements it.

## Microbench / model-comparison gaps

### Q4, Q5, fp16 quantization sweep

The current microbench is at vLLM-native quants. A quantization sweep — same task suite, same model, multiple quants — would put hard data on the "how much quality degrades with smaller quant" question. Each quant level is one model-day of compute.

### Cross-model agentic-flow comparison at the same task suite

Most published "Qwen3.6 vs Claude 4.7 vs GPT-5" comparisons are either single-prompt or short-context. Running the same MMBT Phase B 12-task-family suite against frontier-model APIs (rate-limited and labeled as not-apples-to-apples on cost) would let `SCORECARD.md` extend across the full local-vs-frontier comparison.

### MoE expert-routing characterization

Qwen3.6-35B-A3B is MoE with ~3B active per token. We treat it as a black-box throughput target. Instrumenting expert-routing entropy, expert load imbalance, and expert-cache-hit rate would let us reason about MoE behavior on different hardware properly.

## Methodology / reference-corpus gaps

### CI validation of repo claims vs. data

Right now `findings.md` text can drift from `aggregate/headline.csv` numbers if someone edits one but not the other (the post-merge audit flagged this drift exists). A CI check that regenerates every table from raw cells and fails on doc/CSV mismatch would catch this.

### Schemas for `cell.json`, `manifest.json`, `headline.csv`

JSON Schema files in `schemas/` so any contributor running a new bench can validate their output shape matches. This is what would make MMBT a true reference corpus people contribute to, rather than a single lab's output.

### Status-tag enrichment on `.error` and `.skip-reason` markers

The current `.error` files contain only a string class (`bench-cell-failed`, `server-timeout`). Promoting them to small JSONs (`{class, documented_in, retried, reason}`) makes failure modes legible at the spec level. Half-step started in `qwen3.6-q8-fleet-2026-05-17` with `.skip-reason` text files; full step is to converge both onto a single JSON shape.

### Raw data in artifact store, not git

The `qwen3.6-q8-fleet-2026-05-17` bundle is 109 MB, mostly per-cell 1 Hz power/thermal CSVs. Future bundles will compound. Right place: GitHub Releases, Git LFS, or a sibling `MMBT-data` repo. Git holds aggregates + manifests + a small sample of raw per-cell.

### Independent reproducers

Most claims in `claims.yaml` are tagged `provisional` because the evidence is one study from this lab. Promoting to `strong` requires an independent reproducer. The vendored harness + manifests + claim matrix are the curation work to make that practical.

---

PRs that fill any of the above are explicitly welcomed. Filling the smaller items (schemas, CI, status-tag JSON) doesn't require a hardware fleet — they're pure plumbing. Filling the bigger items requires the matching hardware, but each one is a self-contained PR.
