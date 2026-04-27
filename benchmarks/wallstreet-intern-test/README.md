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

| Model | Entry | Company | Recommendation |
|---|---|---|---|
| GPT-5.5 | `GPT-5.5/` | YETI Holdings (`YETI`) | HOLD / $41 target |

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

The GPT-5.5 entry follows this shape and includes the generated PDF memo and `.xlsx` model.
