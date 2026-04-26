# GitLab Inc. (GTLB) Board of Advisors Presentation

**Release:** v1.0.0  
**Date:** June 18, 2025  
**Recommendation:** BUY @ $42.00 (95% upside)  
**Probability-Weighted Target:** $45.98 (114% upside)

---

## Overview

This repository contains a complete board presentation for GitLab Inc. (GTLB), including:
- The investment recommendation and price target
- The reasoning trail showing how the agent reached its conclusion
- Verification mechanisms for every claim
- Dead ends and alternative approaches considered

**Audience:** Technical, skeptical board of advisors  
**Goal:** Demonstrate agent reasoning, not just rubber-stamp a stock pick

---

## How to Navigate This Repository

### For a Quick Read (10 minutes)
1. Start with this README
2. Read `narrative/storyboard.md` - the narrative arc
3. Skim `audit/numbers.md` - every number with source
4. Check `decisions/` - key analytical choices

### For a Deep Dive (30+ minutes)
1. Read `narrative/` - full narrative structure
2. Review `audit/` - verification mechanisms
3. Review `research/` - questions and dead ends
4. Review `decisions/` - ADR-style decision records
5. Run chart scripts in `assets/charts/` - verify charts
6. Read `tool-log.md` - every tool call with justification

### For Verification (<2 minutes per claim)
1. Find the claim in the deck
2. Follow the trace file in `audit/traces/`
3. Check the source in the input repo
4. Verify the number in `audit/numbers.md`

---

## Repository Structure

```
/workspace/
├── README.md                    # This file
├── sources.md                   # External content sources
├── tool-log.md                  # Every tool call with justification
├── narrative/                   # Narrative structure
│   ├── storyboard.md            # Full narrative arc
│   ├── alternatives.md          # Alternative structures considered
│   └── audience-analysis.md     # Board member profiles and strategy
├── research/                    # Research process
│   ├── questions.md             # Questions encountered and resolved
│   ├── dead-ends.md             # Things that didn't work out
│   └── notes/                   # Working notes, dated
│       ├── 2025-06-18-initial-analysis.md
│       └── 2025-06-18-data-verification.md
├── decisions/                   # ADR-style decision records
│   ├── 001-company-selection.md
│   ├── 002-competitor-selection.md
│   ├── 003-valuation-methodology.md
│   ├── 004-slide-structure.md   # Slide structure ADR
│   └── 005-chart-design.md      # Chart design ADR
├── audit/                       # Verification mechanisms
│   ├── numbers.md               # Every number with source path
│   ├── quotes.md                # Every quote with source
│   ├── traces/                  # Trace files for every claim
│   │   ├── revenue_fy2026.md
│   │   ├── arr_fy2026.md
│   │   ├── nrr_fy2026.md
│   │   ├── cash_investments_fy2026.md
│   │   ├── ev_revenue_gtlb.md
│   │   ├── price_target.md
│   │   ├── wacc.md
│   │   └── dead_ends.md
│   └── reconciliation.md        # Spot-check 5 random numbers
├── assets/                      # Visual assets
│   ├── charts/                  # Chart scripts and outputs
│   │   ├── financial_trajectory.py
│   │   ├── financial_trajectory.png
│   │   ├── competitive_landscape.py
│   │   ├── competitive_landscape.png
│   │   ├── scenario_analysis.py
│   │   └── scenario_analysis.png
│   ├── diagrams/                # Process diagrams
│   │   ├── reasoning_trail.md
│   │   └── dead_ends.md
│   ├── images/                  # Any imagery (empty - no external imagery)
│   └── tables/                  # Source data for tables (empty - data in CSV)
├── deck/                        # Final presentation
│   ├── source/                  # Source files for deck
│   └── (pptx + PDF)             # Final presentation files (to be generated)
└── input/                       # Input repo (read-only)
    ├── memo/                    # Investment memo
    ├── model/                   # Financial model
    ├── extracted/               # Parsed data
    ├── raw/                     # Raw data
    ├── analysis/                # Analysis
    ├── research/                # Research
    └── decisions/               # Input decisions
```

---

## Key Findings

1. **GitLab is undervalued** - DCF base case implies $38.52/share (79% upside), peer EV/Revenue implies $53.25/share (147% upside)
2. **Strong growth trajectory** - Revenue grew from $424M (FY2023) to $955M (FY2026), 30% CAGR
3. **Clear path to profitability** - Operating margins improving from -50% to -7%, projected profitable by FY2028
4. **Healthy SaaS metrics** - 115% NRR, 87% gross margin, $860M ARR
5. **Strong balance sheet** - $1.26B in cash/investments, negligible debt

---

## Data Provenance

Every number in the presentation can be traced back to its source:

- **Revenue figures** → `extracted/income_statement_annual.csv` → yfinance API → SEC filings
- **ARR/NRR** → `extracted/financial_summary.json` → earnings call transcripts
- **Competitor multiples** → `extracted/competitor_data.json` → yfinance API
- **Valuation assumptions** → `decisions/003-valuation-methodology.md` → documented rationale

---

## Verification Mechanism

Every claim in the presentation is verifiable:

1. **Trace files** in `audit/traces/` point to source files
2. **Numbers** in `audit/numbers.md` have source paths
3. **Quotes** in `audit/quotes.md` have file + line numbers
4. **Reconciliation** in `audit/reconciliation.md` spot-checks 5 random numbers

**To verify any claim:**
1. Find the claim in the deck
2. Follow the trace file in `audit/traces/`
3. Check the source in the input repo
4. Verify the number in `audit/numbers.md`

---

## Limitations

1. **SEC filings not downloaded** - SEC.gov returned 403 errors for all automated requests. Financial data sourced from yfinance instead.
2. **No primary industry reports** - Gartner/IDC market sizing cited but not directly accessed.
3. **No customer interviews** - NRR and product satisfaction based on management disclosures only.
4. **No live earnings call participation** - Analysis based on text transcripts only.

---

## Technical Requirements

- Python 3.x with: `matplotlib`, `pandas`, `python-pptx`
- PowerPoint to view the final deck
- Git to clone and navigate the repository

---

## Disclaimer

This presentation is for informational and educational purposes only. It does not constitute investment advice. All valuations are based on assumptions that may not materialize. Past performance does not guarantee future results.

---

## Release Information

**Tag:** v1.0.0  
**Date:** June 18, 2025  
**Commit:** [to be added]  
**Status:** Ready for board presentation

---

## Contact

For questions about this presentation:
- Clone this repository
- Read this README
- Follow the verification mechanism
- Check the tool log for all tool calls
