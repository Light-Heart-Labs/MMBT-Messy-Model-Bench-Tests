# YETI Holdings Investment Memo Repository

This repository is a complete, auditable investment memo package for YETI Holdings (`YETI`). The recommendation is `HOLD`, with the final memo and supporting model included in the repo.

This model entry also includes a follow-on board-of-advisors presentation package at `board-of-advisors-presentation/`. The presentation package is a repo snapshot of the second task: a 20-slide PPTX/PDF deck explaining both the recommendation and the agent's reasoning trail.

Read in this order:

1. `memo/yeti_investment_memo.pdf` for the PM-facing memo.
2. `memo/yeti_investment_memo.md` for the source memo with trace IDs and transcript line links.
3. `analysis/memo_trace_table.csv` to trace each memo number to raw source, extraction artifact, and model cell.
4. `model/yeti_investment_model.xlsx` for the three-statement model, assumptions, valuation, scenarios, sources, and checks.
5. `model/key-outputs.ndjson`, `model/checks-inspect.ndjson`, and `model/formula-error-scan.ndjson` for machine-readable workbook verification.
6. `sources.md` for every fetched URL, timestamp, local path, and SHA-256 hash.
7. `extracted/` for parsed data and extraction scripts connecting raw sources to model inputs.
8. `analysis/` for the sell-side-miss test, competitive analysis, and trace-generation script.
9. `decisions/` for ADR-style records behind non-obvious choices.
10. `research/` for dated working notes, questions, and dead ends.
11. `raw/` for original downloaded filings, transcripts, releases, market pages, and other source files.
12. `board-of-advisors-presentation/` for the follow-on board deck, slide previews, reproducible visuals, and deck-specific audit trail.

## Trace Workflow

To audit a number in the memo:

1. Find the bracketed trace ID, such as `[T003]`.
2. Open `analysis/memo_trace_table.csv` and find that ID.
3. Follow the `source_chain` to the raw file and extraction artifact.
4. Use `model_ref` to locate the related cell in `model/yeti_investment_model.xlsx`.

Management quotes in the memo link to line-numbered transcript text in `extracted/transcripts/`.

## Rebuild Notes

The repo contains generated artifacts as deliverables, so a reader can audit without rebuilding. To rebuild in the same Codex desktop runtime:

1. Run `python extracted\extract_transcripts.py`.
2. Run `python extracted\extract_financials.py`.
3. Run `node model\build_model.mjs` using the bundled Node runtime and `@oai/artifact-tool` dependency.
4. Run `python analysis\build_analysis_artifacts.py`.
5. Run the bundled Python runtime with `memo\render_memo_pdf.py`.

`analysis/download_sources.py` re-fetches public URLs and will update timestamps and hashes in `sources.md`; use it only when intentionally refreshing the evidence base.

Status: complete.
