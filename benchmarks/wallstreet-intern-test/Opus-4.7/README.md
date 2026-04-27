# The Vita Coco Company (NASDAQ: COCO) — Investment memo

**One-line answer:** HOLD with a 12-month price target of **$46** vs. spot **$52.39**.

The repo is the deliverable. A reader should be able to clone it and reconstruct every step of the reasoning. This README is the on-ramp.

## What's here

```
/memo/                  Final memo (PDF + source markdown). Read this first.
/model/                 Three-statement model (xlsx). Toggle Cover!B4 to switch scenarios.
/raw/
  /filings/             Every SEC filing in original HTML format
  /transcripts/         Every earnings call HTML page (Motley Fool / Insider Monkey)
  /other/               EDGAR submissions JSON, XBRL companyfacts, filing-index pages
/extracted/             Parsed financials and transcripts (CSV + line-numbered TXT)
/analysis/              Peer comps + variant view writeup
/research/
  /notes/               Working notes, dated, one file per session
  /questions.md         Running list of questions and how they were resolved
  /dead-ends.md         Things investigated that didn't pan out, with why
/decisions/             ADR-style decision records (numbered)
/scripts/               Every fetch/extract/build/check script. Reproducible.
/sources.md             Every URL fetched, with timestamp and SHA-256
/tool-log.md            Chronological tool calls with one-line justifications
README.md               You are here
```

## Read order

If you have **5 minutes**, read just `memo/COCO_memo.pdf`.

If you have **30 minutes**, also read:
- `decisions/0003-recommendation-and-target.md` — why HOLD, why $46.
- `analysis/variant_view.md` — what sell-side appears to be missing.
- `analysis/peer_comps.md` — peer multiple table.

If you have **2 hours and want to audit the work**, walk:
1. `decisions/0001-target-selection.md` (why this company)
2. `decisions/0002-model-design.md` (why these drivers)
3. `extracted/annual.csv` (FY19-FY25 actuals; every cell carries a `source_accn` pointing at a 10-K in `/raw/filings/`)
4. `extracted/segment_history.csv` (segment x brand splits, parsed from press release tables)
5. `model/coco_model.xlsx` (open Cover, toggle B4 between 1/2/3, watch every line item recompute)
6. `extracted/transcripts/Q4-FY2025_call.txt` (the most-cited transcript — quotes are cited inline by line number throughout the memo)
7. `research/questions.md` and `research/dead-ends.md` (what I wasn't sure about; what I tried that didn't work)

## How to verify the numbers

Every number in the memo points at a path through the repo. Example:

> "FY2025 net sales were $609.8M (+18.2% YoY)"

- `memo/COCO_memo.md` — the claim
- `extracted/annual.csv` row `2025-12-31` — the number
- column `source_accn` = `0001482981-26-000022` — the filing it came from
- `raw/filings/10-K_2025-12-31_26-000022.htm` — the 10-K itself
- `raw/other/edgar_companyfacts_0001482981.json` — the XBRL JSON we parsed
- `sources.md` row 2 — when we fetched the JSON and its SHA-256
- `scripts/extract_financials.py` — the extraction code

End to end in under two minutes.

## How to reproduce the data pulls

```bash
# 1. Verify the data dependencies
python -c "import openpyxl, requests, pandas, reportlab, markdown_it; print('ok')"

# 2. Re-pull EDGAR filings (idempotent; SHA-256 logged to sources.md)
python scripts/fetch_edgar.py submissions 1482981
python scripts/fetch_edgar.py companyfacts 1482981
python scripts/download_filings.py
python scripts/fetch_press_releases.py

# 3. Re-pull transcripts (one-off URLs; see scripts/fetch_transcript.py for usage)

# 4. Run all extraction
python scripts/extract_financials.py
python scripts/extract_press_tables.py
python scripts/build_segment_history.py
python scripts/extract_fool_transcript.py raw/transcripts/<file>.html extracted/transcripts/<file>.txt

# 5. Build model
python scripts/build_model.py

# 6. Verify model internal consistency
python scripts/check_model_balance.py
python scripts/sanity_check_model.py

# 7. Render PDF from markdown
python scripts/md_to_pdf.py memo/COCO_memo.md memo/COCO_memo.pdf
```

## Methodology notes worth knowing before you trust the work

- **The model is granular at segment x brand x year**, but quarterly is held in `extracted/quarterly.csv` and not modeled forward. FY annual grain is appropriate for an investment memo; quarterly noise is below the signal.
- **The exit multiple is the highest-leverage assumption.** Base = 17x EBITDA; Bear = 12x; Bull = 22x. The memo is most sensitive to this. Reasonable analysts could justify ±2-3x off the Base; that moves the price target by ~$8 either way.
- **Live quote data (price, market cap, peer multiples) is from 2026-04-27** but isn't cryptographically verifiable the way SEC content is. Sources.md flags these rows with `n/a (live quote)`.
- **The memo cites transcript files by line number** like `transcripts/Q4-FY2025_call.txt:46`. The line-numbered transcripts are the citable artifacts; the original HTML in `raw/transcripts/` exists for SHA verification.

## Scope and tooling

Built on Windows 11 + Git Bash + Python 3.13. The brief mentioned a Linux VM; the work is shell-portable and the only Windows concession is path style in some Bash invocations. No external paid data — everything fetched is from SEC EDGAR (free) or public web.

LLM disclosure: this entire repo was assembled in a single research session by Claude Opus 4.7 (1M context). The memo, ADRs, and analysis are first-draft and unedited by a human. The model formulas were independently re-implemented in Python (`scripts/sanity_check_model.py`) and produce identical Base/Bear/Bull outputs to the xlsx, which mitigates "the spreadsheet says something different than the memo claims" risk.

## License

This is research output, not investment advice. Don't trade off it without doing your own work. The repository is provided as-is, no warranty.
