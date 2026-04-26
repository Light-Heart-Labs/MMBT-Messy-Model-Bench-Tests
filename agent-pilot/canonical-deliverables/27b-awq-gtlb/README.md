# GitLab Inc. (GTLB) Investment Memo

**Recommendation: BUY** | **12-Month Price Target: $42.00** | **Current Price: $21.51**

This repository contains a complete investment analysis of GitLab Inc. (NYSE: GTLB), a DevOps platform provider with a $3.66B market cap.

## How to Navigate This Repository

### For a Quick Read (15 minutes)
1. Start with [`memo/gitlab_investment_memo.md`](memo/gitlab_investment_memo.md) — the final investment memo
2. Skim [`model/gitlab_three_statement_model.xlsx`](model/gitlab_three_statement_model.xlsx) — the financial model (Valuation sheet)
3. Check [`decisions/`](decisions/) — key analytical choices made

### For a Deep Dive (1-2 hours)
1. Read the memo first
2. Review the financial model in detail:
   - `model/gitlab_three_statement_model.xlsx` — three-statement model with projections
   - Sheets: Assumptions, Income Statement, Balance Sheet, Cash Flow, Valuation, Scenarios
3. Trace numbers back to sources:
   - `extracted/` — parsed financial data from yfinance
   - `raw/transcripts/` — earnings call transcripts from Seeking Alpha
4. Review the analysis:
   - `analysis/gitlab_analysis.py` — analytical notebook
   - `analysis/analysis_summary.md` — key findings summary
5. Understand the reasoning:
   - `decisions/` — ADR-style decision records for key choices
   - `research/questions.md` — questions encountered and how they were resolved
   - `research/dead-ends.md` — things that didn't work out
6. Audit the sources:
   - `sources.md` — every URL fetched with timestamps and SHA hashes
   - `tool-log.md` — every tool call made during research

## Repository Structure

```
/workspace/
├── README.md                    # This file
├── sources.md                   # All URLs with timestamps and SHA hashes
├── tool-log.md                  # Every tool call with justification
├── memo/
│   └── gitlab_investment_memo.md  # Final investment memo (markdown source)
├── model/
│   └── gitlab_three_statement_model.xlsx  # Three-statement financial model
├── raw/
│   ├── filings/                 # SEC filings (attempted, mostly blocked by 403)
│   │   ├── cik_filings_index.json
│   │   └── test.html
│   ├── transcripts/             # Earnings call transcripts (6 files, Q4 2023 - Q1 2025)
│   │   ├── GTLB_Q4_2023_transcript.html
│   │   ├── GTLB_Q4_2023_transcript.txt
│   │   ├── GTLB_Q1_2024_transcript.html
│   │   ├── GTLB_Q1_2024_transcript.txt
│   │   ├── GTLB_Q2_2024_transcript.html
│   │   ├── GTLB_Q2_2024_transcript.txt
│   │   ├── GTLB_Q3_2024_transcript.html
│   │   ├── GTLB_Q3_2024_transcript.txt
│   │   ├── GTLB_Q4_2024_transcript.html
│   │   ├── GTLB_Q4_2024_transcript.txt
│   │   ├── GTLB_Q1_2025_transcript.html
│   │   └── GTLB_Q1_2025_transcript.txt
│   └── other/                   # Other primary sources (empty - sources blocked)
├── extracted/                   # Parsed/cleaned data
│   ├── income_statement_annual.csv
│   ├── income_statement_quarterly.csv
│   ├── balance_sheet_annual.csv
│   ├── cash_flow_annual.csv
│   ├── company_info.json
│   ├── competitor_data.json
│   ├── financial_summary.json
│   ├── earnings_dates.csv
│   ├── historical_prices.csv
│   ├── analyst_recommendations.csv
│   ├── institutional_holders.csv
│   └── major_holders.csv
├── analysis/
│   ├── gitlab_analysis.py       # Analytical notebook
│   └── analysis_summary.md      # Key findings summary
├── research/
│   ├── notes/
│   │   └── 2025-06-18-company-selection.md  # Company selection notes
│   ├── questions.md             # Questions encountered and resolved
│   └── dead-ends.md             # Things that didn't work out
└── decisions/
    ├── 001-company-selection.md  # Why GitLab was selected
    ├── 002-competitor-selection.md  # Why these competitors were chosen
    └── 003-valuation-methodology.md  # Why DCF + EV/Revenue was used
```

## Key Findings

1. **GitLab is undervalued** — DCF base case implies $38.52/share (79% upside), peer EV/Revenue implies $53.25/share (147% upside)
2. **Strong growth trajectory** — Revenue grew from $424M (FY2023) to $955M (FY2026), 30% CAGR
3. **Clear path to profitability** — Operating margins improving from -50% to -7%, projected profitable by FY2028
4. **Healthy SaaS metrics** — 115% NRR, 87% gross margin, $860M ARR
5. **Strong balance sheet** — $1.26B in cash/investments, negligible debt

## Data Provenance

Every number in the memo can be traced back to its source:

- **Revenue figures** → `extracted/income_statement_annual.csv` → yfinance API → SEC filings
- **ARR/NRR** → `raw/transcripts/GTLB_Q*_transcript.txt` → Seeking Alpha earnings call transcripts
- **Competitor multiples** → `extracted/competitor_data.json` → yfinance API
- **Valuation assumptions** → `decisions/003-valuation-methodology.md` → documented rationale

## Limitations

1. **SEC filings not downloaded** — SEC.gov returned 403 errors for all automated requests. Financial data sourced from yfinance instead.
2. **No primary industry reports** — Gartner/IDC market sizing cited but not directly accessed.
3. **No customer interviews** — NRR and product satisfaction based on management disclosures only.
4. **No live earnings call participation** — Analysis based on text transcripts only.

## Technical Requirements

- Python 3.x with: `yfinance`, `pandas`, `openpyxl`, `requests`, `beautifulsoup4`, `lxml`
- Excel or LibreOffice to view the financial model

## Disclaimer

This memo is for informational and educational purposes only. It does not constitute investment advice. All valuations are based on assumptions that may not materialize. Past performance does not guarantee future results.
