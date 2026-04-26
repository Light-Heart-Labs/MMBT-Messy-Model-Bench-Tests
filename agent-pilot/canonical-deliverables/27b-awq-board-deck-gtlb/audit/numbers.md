# Numbers Audit Trail

Every number in the deck, with its source path in the input repo.

## Slide 1: Recommendation & Price Target

| Number | Claim | Source Path |
|--------|-------|-------------|
| $21.51 | Current price | `/input/repo/extracted/company_info.json` → `currentPrice` |
| $42.00 | 12-month price target | `/input/repo/memo/gitlab_investment_memo.md` → "12-Month Price Target" section |
| 95% | Upside from current | Calculated: ($42.00 - $21.51) / $21.51 = 95.3% |
| $45.98 | Probability-weighted target | `/input/repo/memo/gitlab_investment_memo.md` → "Scenario Analysis" table |
| 114% | Weighted upside | Calculated: ($45.98 - $21.51) / $21.51 = 113.8% |
| $3.66B | Market cap | `/input/repo/extracted/company_info.json` → `marketCap` |

## Slide 2: Thesis

| Number | Claim | Source Path |
|--------|-------|-------------|
| $30B+ | DevOps TAM | `/input/repo/memo/gitlab_investment_memo.md` → "Large and Growing TAM" |
| 15-20% | TAM growth rate | `/input/repo/memo/gitlab_investment_memo.md` → "Large and Growing TAM" |
| 115% | NRR | `/input/repo/extracted/financial_summary.json` → `nrr[4]` |
| $860M | ARR | `/input/repo/extracted/financial_summary.json` → `arr[4]` |
| -7.4% | FY2026 op margin | `/input/repo/extracted/income_statement_annual.csv` → Operating Income / Revenue |
| $1.26B | Cash & investments | `/input/repo/extracted/balance_sheet_annual.csv` → Cash Cash Equivalents And Short Term Investments |

## Slide 3: Thesis Breakers

| Number | Claim | Source Path |
|--------|-------|-------------|
| 110% | NRR threshold | `/input/repo/memo/gitlab_investment_memo.md` → "NRR Decline" risk |
| 120% | Historical NRR peak | `/input/repo/extracted/financial_summary.json` → `nrr[0]` |
| 115% | Current NRR | `/input/repo/extracted/financial_summary.json` → `nrr[4]` |

## Slide 4: Financial Trajectory

| Number | Claim | Source Path |
|--------|-------|-------------|
| $424M | FY2023 revenue | `/input/repo/extracted/income_statement_annual.csv` → Total Revenue, 2023-01-31 |
| $580M | FY2024 revenue | `/input/repo/extracted/income_statement_annual.csv` → Total Revenue, 2024-01-31 |
| $759M | FY2025 revenue | `/input/repo/extracted/income_statement_annual.csv` → Total Revenue, 2025-01-31 |
| $955M | FY2026 revenue | `/input/repo/extracted/income_statement_annual.csv` → Total Revenue, 2026-01-31 |
| -49.8% | FY2023 op margin | `/input/repo/extracted/financial_summary.json` → op_income[1]/revenue[1] |
| -32.3% | FY2024 op margin | `/input/repo/extracted/financial_summary.json` → op_income[2]/revenue[2] |
| -18.8% | FY2025 op margin | `/input/repo/extracted/financial_summary.json` → op_income[3]/revenue[3] |
| -7.4% | FY2026 op margin | `/input/repo/extracted/financial_summary.json` → op_income[4]/revenue[4] |
| $33M | FY2024 FCF | `/input/repo/extracted/financial_summary.json` → fcf[2] |
| $222M | FY2026 FCF | `/input/repo/extracted/financial_summary.json` → fcf[4] |

## Slide 5: SaaS Metrics

| Number | Claim | Source Path |
|--------|-------|-------------|
| $300M | FY2022 ARR | `/input/repo/extracted/financial_summary.json` → arr[0] |
| $400M | FY2023 ARR | `/input/repo/extracted/financial_summary.json` → arr[1] |
| $530M | FY2024 ARR | `/input/repo/extracted/financial_summary.json` → arr[2] |
| $680M | FY2025 ARR | `/input/repo/extracted/financial_summary.json` → arr[3] |
| $860M | FY2026 ARR | `/input/repo/extracted/financial_summary.json` → arr[4] |
| 120% | FY2022 NRR | `/input/repo/extracted/financial_summary.json` → nrr[0] |
| 118% | FY2023 NRR | `/input/repo/extracted/financial_summary.json` → nrr[1] |
| 117% | FY2024 NRR | `/input/repo/extracted/financial_summary.json` → nrr[2] |
| 116% | FY2025 NRR | `/input/repo/extracted/financial_summary.json` → nrr[3] |
| 115% | FY2026 NRR | `/input/repo/extracted/financial_summary.json` → nrr[4] |
| 87.4% | FY2026 gross margin | `/input/repo/extracted/financial_summary.json` → gross_profit[4]/revenue[4] |
| $572M | Deferred revenue | `/input/repo/extracted/balance_sheet_annual.csv` → Current Deferred Revenue + Non Current Deferred Revenue |

## Slide 6: Competitive Position

| Number | Claim | Source Path |
|--------|-------|-------------|
| 2.56x | GTLB EV/Revenue | `/input/repo/extracted/competitor_data.json` → GTLB.ev_revenue |
| 7.03x | Peer avg EV/Revenue | Calculated from `/input/repo/extracted/competitor_data.json` (excl. GTLB) |
| 23.2% | GTLB revenue growth | `/input/repo/extracted/competitor_data.json` → GTLB.revenue_growth |

## Slide 7: Mispricing Thesis

| Number | Claim | Source Path |
|--------|-------|-------------|
| $38.52 | DCF base case | `/input/repo/memo/gitlab_investment_memo.md` → "Implied Price: $38.52" |
| $53.25 | Peer EV/Revenue implied | `/input/repo/memo/gitlab_investment_memo.md` → "Implied Price: $53.25" |
| 2.56x | Current EV/Revenue | `/input/repo/extracted/competitor_data.json` → GTLB.ev_revenue |
| 7.03x | Peer average | Calculated from competitor data |
| 3.5x | Target EV/Revenue | Calculated: $42.00 target implies ~3.5x FY2027E EV/Revenue |

## Slide 8: Risk Assessment

| Number | Claim | Source Path |
|--------|-------|-------------|
| 0.75 | NRR decline probability | Estimated from trend (120%→115% over 4 years) |
| 0.90 | NRR decline impact | High impact on revenue growth |
| 0.50 | GitHub competition probability | Medium probability |
| 0.85 | GitHub competition impact | High impact on market share |

## Slide 9: Scenario Distribution

| Number | Claim | Source Path |
|--------|-------|-------------|
| $18.58 | Bear case price | `/input/repo/memo/gitlab_investment_memo.md` → "Scenario Analysis" table |
| 25% | Bear probability | `/input/repo/memo/gitlab_investment_memo.md` → "Scenario Analysis" table |
| $38.52 | Base case price | `/input/repo/memo/gitlab_investment_memo.md` → "Scenario Analysis" table |
| 50% | Base probability | `/input/repo/memo/gitlab_investment_memo.md` → "Scenario Analysis" table |
| $88.30 | Bull case price | `/input/repo/memo/gitlab_investment_memo.md` → "Scenario Analysis" table |
| 25% | Bull probability | `/input/repo/memo/gitlab_investment_memo.md` → "Scenario Analysis" table |
| $45.98 | Weighted target | `/input/repo/memo/gitlab_investment_memo.md` → "Probability-Weighted" |

## Slide 15: Recommendation & Next Steps

| Number | Claim | Source Path |
|--------|-------|-------------|
| 2-3% | Position sizing | `/input/repo/memo/gitlab_investment_memo.md` → "Position sizing" |
| 12 months | Holding period | `/input/repo/memo/gitlab_investment_memo.md` → "12-month holding period" |
