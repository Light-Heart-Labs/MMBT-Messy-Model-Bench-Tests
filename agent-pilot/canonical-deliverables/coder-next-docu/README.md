# DocuSign Investment Memo Repository

This repository contains a complete investment memo on DocuSign, Inc. (DOCU), including financial models, competitive analysis, and risk assessment.

## Repository Structure

```
/investment-memo/
├── memo/                          # Final memo (PDF + source markdown)
│   ├── docusign_investment_memo.md    # Main memo (Markdown)
│   └── docusign_investment_memo.html  # HTML version
├── model/                         # Three-statement financial model (xlsx)
│   └── docusign_three_statement_model.xlsx
├── raw/                           # Raw data sources
│   ├── filings/                   # SEC filings (10-K, 10-Q, 8-K, DEF 14A)
│   ├── transcripts/               # Earnings transcripts (8-K press releases)
│   └── other/                     # Other primary sources
├── extracted/                     # Parsed/cleaned data from raw sources
│   ├── 10-K_fy2026_metrics.txt    # Key financial metrics
│   └── scripts/                   # Extraction scripts
├── analysis/                      # Notebooks and scripts for analysis
│   ├── dcf_analysis.py            # DCF analysis script
│   └── dcf_analysis_results.txt   # DCF analysis results
├── research/                      # Research notes and documentation
│   ├── notes/                     # Working notes (dated)
│   ├── questions.md               # Running list of questions and answers
│   └── dead-ends.md               # Dead ends and why they didn't pan out
├── decisions/                     # ADR-style decision records
│   ├── 001-company-selection.md
│   ├── 002-multiple-selection.md
│   ├── 003-discount-rate-selection.md
│   └── 004-terminal-growth-selection.md
├── sources.md                     # Every URL fetched with timestamp and SHA
├── tool-log.md                    # Every tool call in order
└── README.md                      # This file
```

## How to Navigate This Repository

### For a Quick Overview (15 minutes)

1. **Start with the memo**: Read `memo/docusign_investment_memo.md`
   - Executive summary
   - Investment thesis
   - Financial analysis
   - Valuation
   - Risk assessment
   - Buy/Hold/Sell recommendation

2. **Check the recommendation**: Page 1 clearly states BUY with $72 price target

### For Detailed Analysis (1 hour)

1. **Review the financial model**: `model/docusign_three_statement_model.xlsx`
   - Income statement, balance sheet, cash flow statement
   - Historical data and projections

2. **Examine the DCF analysis**: `analysis/dcf_analysis_results.txt`
   - Key assumptions
   - Financial projections
   - Valuation ranges

3. **Review decision records**: `decisions/` directory
   - Company selection rationale
   - Valuation multiple selection
   - Discount rate assumptions
   - Terminal growth assumptions

### For Audit Trail (2 hours)

1. **Trace data sources**: `sources.md`
   - Every URL fetched
   - Timestamp and SHA of content

2. **Follow the data pipeline**: 
   - Raw filings: `raw/filings/`
   - Extracted metrics: `extracted/10-K_fy2026_metrics.txt`
   - Model cells: `model/docusign_three_statement_model.xlsx`
   - Memo claims: `memo/docusign_investment_memo.md`

3. **Review research notes**: `research/notes/`
   - dated files showing research progression
   - questions and answers
   - dead ends and why they didn't pan out

## Key Findings

- **Recommendation**: BUY
- **12-Month Price Target**: $72.00 (30% upside from current $55.40)
- **DCF Target**: $104.82 (base case)
- **Bear Case**: $77.48
- **Bull Case**: $132.36

## Data Traceability

Every number in the memo is traceable:
1. **Financial metrics** → SEC filings (10-K, 10-Q, 8-K)
2. **Competitive data** → SEC filings (competitor 10-Ks), industry reports
3. **Valuation assumptions** → Decision records (ADRs)
4. **Research notes** → Research notes (dated files)

## Disclaimer

This memo is for informational purposes only and does not constitute investment advice. All data is traceable to public sources as documented in the `sources.md` file and appendix of the memo.
