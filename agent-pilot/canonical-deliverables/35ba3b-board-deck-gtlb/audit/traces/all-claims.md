# Audit Traces — Every Claim in the Deck

## Slide 1: Recommendation and Price Target

### Claim: "BUY recommendation, $42 price target, 95% upside"
- **Trace file:** `/audit/traces/slide1_recommendation.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** Line 3 (header), Line 10 (recommendation section)
- **Commit:** See `/input/repo/.git/` — final commit contains the memo

### Claim: "Current Price: $21.51"
- **Trace file:** `/audit/traces/slide1_current_price.md`
- **Source:** `/input/repo/extracted/company_info.json`
- **Location:** `"currentPrice": 21.51`
- **Also in:** `/input/repo/memo/gitlab_investment_memo.md` line 4

### Claim: "Market Cap: $3.66B"
- **Trace file:** `/audit/traces/slide1_market_cap.md`
- **Source:** `/input/repo/extracted/company_info.json`
- **Location:** `"marketCap": 3659539456`
- **Also in:** `/input/repo/memo/gitlab_investment_memo.md` line 5

## Slide 2: The Thesis

### Claim: "Revenue grew from $424M (FY2023) to $955M (FY2026), 30% CAGR"
- **Trace file:** `/audit/traces/slide2_revenue_growth.md`
- **Source:** `/input/repo/extracted/income_statement_annual.csv`
- **Location:** Row "Total Revenue", columns "2023-01-31" ($424,336,000) and "2026-01-31" ($955,224,000)
- **Also in:** `/input/repo/extracted/financial_summary.json` revenue array

### Claim: "Operating margins improving from -49.8% to -7.4%"
- **Trace file:** `/audit/traces/slide2_operating_margin.md`
- **Source:** `/input/repo/extracted/income_statement_annual.csv`
- **Location:** Row "Total Operating Income As Reported" and "Total Revenue"
- **Calculation:** FY2023: -211,411,000 / 424,336,000 = -49.8%; FY2026: -70,481,000 / 955,224,000 = -7.4%

### Claim: "115% NRR, $860M ARR"
- **Trace file:** `/audit/traces/slide2_saas_metrics.md`
- **Source:** `/input/repo/extracted/financial_summary.json`
- **Location:** `"arr": [..., 860]`, `"nrr": [..., 115]`
- **Also in:** Earnings call transcripts `/input/repo/raw/transcripts/GTLB_Q4_2024_transcript.txt`

### Claim: "$1.26B cash/investments, negligible debt"
- **Trace file:** `/audit/traces/slide2_balance_sheet.md`
- **Source:** `/input/repo/extracted/balance_sheet_annual.csv`
- **Location:** Row "Cash Cash Equivalents And Short Term Investments" for 2026-01-31: $1,259,903,000
- **Debt:** Row "Total Debt" for 2026-01-31: $187,000

## Slide 3: What Would Change the Recommendation

### Claim: "NRR < 110% would slow growth significantly"
- **Trace file:** `/audit/traces/slide3_nrr_threshold.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** Risk Assessment section, point 1

### Claim: "GitHub Copilot eating share would erode market position"
- **Trace file:** `/audit/traces/slide3_github_competition.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** Risk Assessment section, point 2

### Claim: "Macro recession could delay purchases"
- **Trace file:** `/audit/traces/slide3_macro_risk.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** Risk Assessment section, point 3

## Slide 4: Financial Trajectory

### Claim: "Revenue: $424M (FY2023) → $580M (FY2024) → $759M (FY2025) → $955M (FY2026)"
- **Trace file:** `/audit/traces/slide4_revenue.md`
- **Source:** `/input/repo/extracted/income_statement_annual.csv`
- **Location:** Row "Total Revenue"

### Claim: "FCF: -$84M (FY2023) → $33M (FY2024) → -$68M (FY2025) → $222M (FY2026)"
- **Trace file:** `/audit/traces/slide4_fcf.md`
- **Source:** `/input/repo/extracted/cash_flow_annual.csv`
- **Location:** Row "Free Cash Flow"

### Claim: "Gross margin stable at 87-90%"
- **Trace file:** `/audit/traces/slide4_gross_margin.md`
- **Source:** `/input/repo/extracted/income_statement_annual.csv`
- **Location:** Row "Gross Profit" / Row "Total Revenue"

## Slide 5: Competitive Position

### Claim: "GitLab EV/Revenue: 2.56x"
- **Trace file:** `/audit/traces/slide5_gtlb_ev_rev.md`
- **Source:** `/input/repo/extracted/competitor_data.json`
- **Location:** `"GTLB": {"ev_revenue": 2.559}`

### Claim: "Peer average EV/Revenue: 7.03x"
- **Trace file:** `/audit/traces/slide5_peer_avg.md`
- **Source:** `/input/repo/extracted/competitor_data.json`
- **Location:** Average of TEAM (3.215), DDOG (12.388), MDB (7.329), CFLT (8.686), SNOW (10.069), ZS (6.711), OKTA (3.884), BILL (2.143)

## Slide 6: Mispricing Thesis

### Claim: "Sell-side consensus: $30.79"
- **Trace file:** `/audit/traces/slide6_consensus.md`
- **Source:** `/input/repo/extracted/company_info.json`
- **Location:** `"targetMeanPrice": 30.79167`

### Claim: "DCF base case: $38.52"
- **Trace file:** `/audit/traces/slide6_dcf_base.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** DCF Analysis section, "Implied Price: $38.52"

## Slide 7: Risk Assessment

### Claim: "NRR decline from 120% to 115%"
- **Trace file:** `/audit/traces/slide7_nrr_decline.md`
- **Source:** `/input/repo/extracted/financial_summary.json`
- **Location:** `"nrr": [120, 118, 117, 116, 115]`

## Slide 8: Bear/Base/Bull Scenarios

### Claim: "Bear: $18.58 (25%), Base: $38.52 (50%), Bull: $88.30 (25%)"
- **Trace file:** `/audit/traces/slide8_scenarios.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** Scenario Analysis table

### Claim: "Probability-weighted target: $45.98"
- **Trace file:** `/audit/traces/slide8_weighted.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** "Probability-Weighted: $45.98"
- **Calculation:** 0.25 * 18.58 + 0.50 * 38.52 + 0.25 * 88.30 = 4.645 + 19.26 + 22.075 = 45.98

## Slide 9: DCF Bridge

### Claim: "WACC: 10.5%"
- **Trace file:** `/audit/traces/slide9_wacc.md`
- **Source:** `/input/repo/decisions/003-valuation-methodology.md`
- **Location:** "WACC of 10.5%"

### Claim: "Terminal growth: 3.0%"
- **Trace file:** `/audit/traces/slide9_terminal.md`
- **Source:** `/input/repo/decisions/003-valuation-methodology.md`
- **Location:** "Terminal growth of 3.0%"

## Slide 10: Reasoning Trail

### Claim: "6 earnings call transcripts downloaded"
- **Trace file:** `/audit/traces/slide10_transcripts.md`
- **Source:** `/input/repo/raw/transcripts/`
- **Location:** 6 .txt files (Q4 2023 through Q1 2025)

### Claim: "3 ADRs documented"
- **Trace file:** `/audit/traces/slide10_adrs.md`
- **Source:** `/input/repo/decisions/`
- **Location:** 001-company-selection.md, 002-competitor-selection.md, 003-valuation-methodology.md

## Slide 11: Dead Ends

### Claim: "5 dead ends documented"
- **Trace file:** `/audit/traces/slide11_dead_ends.md`
- **Source:** `/input/repo/research/dead-ends.md`
- **Location:** 5 sections (SEC filings, IR website, PRNewswire, CIK lookup, audio)

## Slide 12: Confidence & Limitations

### Claim: "Revenue trajectory: confident"
- **Trace file:** `/audit/traces/slide12_revenue_confidence.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** "What We're Confident About" → "Revenue trajectory"

### Claim: "ARR and NRR: estimating"
- **Trace file:** `/audit/traces/slide12_arr_confidence.md`
- **Source:** `/input/repo/memo/gitlab_investment_memo.md`
- **Location:** "What We're Estimating" → "ARR and NRR"

## Slide 13: How to Audit This Deck

### Claim: "Every claim traces to a file in /input/repo/"
- **Trace file:** `/audit/traces/slide13_audit_mechanism.md`
- **Source:** This file (`/audit/traces/`)
- **Location:** All trace files above

## Slide 14: Number Reconciliation

### See `/audit/reconciliation.md` for spot-check reconciliation of 5 random numbers.
