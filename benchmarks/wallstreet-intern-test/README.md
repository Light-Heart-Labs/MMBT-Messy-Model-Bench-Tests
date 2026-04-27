# Wallstreet Intern Test Benchmark

## Prompt

Build a complete investment memo on any publicly traded US company with a market cap between $1B and $10B. The deliverable must be a git repository with a final memo, three-statement model, raw primary sources, extracted data, analysis, questions, dead ends, decision records, source hashes, and a tool log. Every number in the memo must be traceable from raw source to model to memo.

## Why This Is A Messy Benchmark

This task combines:

- live public-company source gathering,
- SEC filing and transcript extraction,
- financial modeling,
- valuation and recommendation judgment,
- source hashing and auditability,
- PDF and spreadsheet artifact generation,
- governance artifacts such as ADRs, questions, and dead ends.

The output is not only an answer. The model has to construct a self-contained research repository that a stranger can audit.

## Model Entries

| Model | Entry | Company | Recommendation | Shipped Rate (N=3) | Follow-On |
|---|---|---|---|---|---|
| GPT-5.5 (cloud) | [`GPT-5.5/`](GPT-5.5/) | YETI Holdings (`YETI`) | HOLD / $41 target | (cloud — single shipped run published) | [`GPT-5.5/board-of-advisors-presentation/`](GPT-5.5/board-of-advisors-presentation/) |
| Opus-4.7 (cloud) | [`Opus-4.7/`](Opus-4.7/) | (see entry README) | (see entry README) | (cloud) | — |
| Qwen3.6-27B-AWQ (local) | [`Qwen3.6-27B-AWQ/`](Qwen3.6-27B-AWQ/) | GitLab Inc. (`GTLB`) | BUY | **1 of 3** runs shipped | — |
| Qwen3-Coder-Next-AWQ (local) | [`Qwen3-Coder-Next-AWQ/`](Qwen3-Coder-Next-AWQ/) | DocuSign, Inc. (`DOCU`) | BUY | **1 of 3** runs shipped | — |
| Qwen3.6-35B-A3B-AWQ (local) | [`Qwen3.6-35B-A3B-AWQ/`](Qwen3.6-35B-A3B-AWQ/) | — | (no usable deliverable) | **0 of 3** runs shipped | — |

The local-model entries are *cherry-picked successful runs* (where any shipped). The other 2 of 3 attempts per model are described in each entry's README — they're a real part of the comparison story, not noise to filter out. See the cross-cutting findings doc at [`../dreamserver-75-pr-audit/findings-2026-04-27-local-models.md`](../dreamserver-75-pr-audit/findings-2026-04-27-local-models.md) for the broader local-vs-cloud comparison; the same shipped-rate gap applies here.

## Expected Entry Shape

Each model entry should preserve the artifact structure requested by the benchmark prompt:

- `memo/`
- `model/`
- `raw/`
- `extracted/`
- `analysis/`
- `research/`
- `decisions/`
- `sources.md`
- `tool-log.md`
- `README.md`

The cloud entries (`GPT-5.5/`, `Opus-4.7/`) follow this shape with both the generated PDF memo and the `.xlsx` model. The local entries follow the same shape but produce markdown-only memos (no PDF rendering); the local Coder-Next entry doesn't ship the machine-readable model-verification ndjson files (`key-outputs.ndjson`, `checks-inspect.ndjson`, `formula-error-scan.ndjson`) that the cloud entries include.

The GPT-5.5 entry also includes a follow-on board-of-advisors presentation package in `GPT-5.5/board-of-advisors-presentation/`. That package is a separate auditable repo snapshot that turns the memo into a 20-slide board discussion deck with PPTX/PDF outputs, reproducible chart scripts, slide-level trace files, quote context, number audit, reconciliation checks, and ADRs for presentation decisions. Local models have separately produced board-deck artifacts in the source bench repo (the `task_board_presentation.md` task, runs `27b_board_pres_v{1..3}` and `coder_board_pres_v{1..3}`) but those aren't packaged here as part of the wallstreet entries.
