# Research Notes — Session 1: Input Repo Analysis
**Date:** 2026-04-26
**Topic:** Understanding the input repo structure and extracting key data

## Key Findings

### Input Repo Structure
The input repo contains a complete investment analysis of GitLab Inc. (GTLB):
- **Memo:** Final investment memo with BUY recommendation, $42 target
- **Financial data:** 5 years of annual income statement, balance sheet, cash flow
- **SaaS metrics:** ARR ($860M FY2026), NRR (115%), gross margin (87.4%)
- **Competitor data:** 10 companies with market cap, EV/Revenue, margins
- **Historical prices:** Daily prices from Aug 2025 to Apr 2026
- **Transcripts:** 6 earnings call transcripts (Q4 2023 - Q1 2025)
- **Decisions:** 3 ADRs (company selection, competitor selection, valuation methodology)
- **Dead ends:** 5 failed approaches (SEC filings, IR website, PRNewswire, CIK lookup, audio)
- **Questions:** 8 questions with resolutions

### Key Numbers to Trace
- Revenue: $424M (FY2023) → $955M (FY2026)
- Operating margin: -49.8% → -7.4%
- FCF: -$84M (FY2023) → $222M (FY2026)
- ARR: $400M → $860M
- NRR: 118% → 115%
- Cash: $295M → $230M (declining due to investments)
- Shares: 151.1M → 170.1M
- Current price: $21.51
- Market cap: $3.66B
- DCF base case: $38.52
- Peer EV/Revenue: $53.25
- Bear: $18.58, Base: $38.52, Bull: $88.30
- Probability-weighted: $45.98
- 12-month target: $42.00

### Data Sources
- Financial data: yfinance (derived from SEC filings)
- ARR/NRR: Earnings call transcripts (Seeking Alpha)
- Competitor data: yfinance
- Historical prices: yfinance

### Limitations to Surface
- SEC filings blocked (403 errors)
- No primary industry reports accessed
- No customer interviews
- ARR/NRR are management metrics, not GAAP
