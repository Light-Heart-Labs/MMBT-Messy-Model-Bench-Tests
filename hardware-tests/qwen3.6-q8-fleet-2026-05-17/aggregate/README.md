# Aggregate tables — read order

The five files in this directory differ in **scope** and **load-bearing-ness**. Use this table to pick the right one for your reading purpose.

| file | scope | use it for |
|---|---|---|
| **`canonical-headline.csv` / `.json`** | Same-source-SHA cross-host ranking. One row per (host, model, native llama.cpp backend). | Citing the **single-user cross-host hardware ranking**. This is the table whose claims appear in `findings.md § Headline hardware ranking` and `claims.yaml`. |
| **`appendix-headline.csv` / `.json`** | Same-host non-canonical runs. Carries `appendix_status` (e.g. `supplementary`, `engine-comparison`) and `appendix_reason` per row. | Reading the dual-card supplementary or vLLM/FP8 engine-comparison rows. **Do NOT mix into a cross-host comparison** — different backend or different quant. |
| `headline.csv` / `.json` | All rows above, unsplit. | Backwards compatibility for tooling that scripted against the original file shape. New consumers should prefer the split files. |
| `cells.jsonl` | One row per (host, model, backend, cell) — all 355 cells across the grid. | Per-cell drill-downs, re-deriving the headline tables, building custom plots. |
| `all-inferences.jsonl` | One row per inference (~6400 rows) with content SHA, prompt tokens, gen tokens, decode tps, prefill tps, ttft ms. | Generation-level analysis, determinism checks, semantic spot-checks. |
| `determinism.tsv` | Cross-host SHA equality table for inferences run on ≥2 hosts. | The "do different platforms produce byte-identical output at temperature=0?" question. |

## Status vocabulary in the appendix table

| `appendix_status` | meaning |
|---|---|
| `supplementary` | Same engine, different hardware configuration (e.g. dual-card vs single-card on Tower2). Reported separately because it's not the canonical cross-host operating point. |
| `engine-comparison` | Different *engine* (e.g. vLLM/FP8 vs llama.cpp/Q8). Reported because the cross-engine delta is informative, but **the cross-host ranking holds the engine fixed** by definition, so engine-comparison rows live in the appendix. |
| `retracted` | Has data on disk but is excluded from claims due to a known kernel/build/engine bug. The Tower2 35B-A3B native CUDA cells (SOFT_MAX kernel crash) are retracted at the cells.jsonl level — they have zero-throughput rows but no headline entry. |

## Why two files (canonical + appendix) instead of one with a flag

The original `headline.csv` mixed all rows and required readers to know which backends were canonical. A reviewer reasonably flagged that as a footgun — `manifest.json` is the only place that tagged the appendix nature, and a copy-paste of `headline.csv` into a spreadsheet would silently include Tower2 dual-card numbers as if they were part of the cross-host ranking. The split files remove that footgun: anyone who opens `canonical-headline.csv` is looking at exactly the rows that should appear in a cross-host hardware comparison.
