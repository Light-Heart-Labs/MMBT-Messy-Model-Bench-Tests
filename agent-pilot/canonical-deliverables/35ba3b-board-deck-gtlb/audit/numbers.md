# Numbers in the Deck — Every Number with Source Path

## Slide 1: Recommendation

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| $42.00 | 1 | `/input/repo/memo/gitlab_investment_memo.md` | Line 3, Line 10 |
| $21.51 | 1 | `/input/repo/extracted/company_info.json` | `"currentPrice": 21.51` |
| $3.66B | 1 | `/input/repo/extracted/company_info.json` | `"marketCap": 3659539456` |
| 95% | 1 | `/input/repo/memo/gitlab_investment_memo.md` | Line 10: "95% upside" |
| 7/10 | 1 | Derived | Confidence assessment from memo limitations |

## Slide 2: Thesis

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| $424M | 2 | `/input/repo/extracted/income_statement_annual.csv` | Total Revenue, 2023-01-31: 424,336,000 |
| $955M | 2 | `/input/repo/extracted/income_statement_annual.csv` | Total Revenue, 2026-01-31: 955,224,000 |
| 30% CAGR | 2 | Derived | CAGR from $424M to $955M over 3 years |
| -49.8% | 2 | `/input/repo/extracted/income_statement_annual.csv` | Op Income / Revenue FY2023 |
| -7.4% | 2 | `/input/repo/extracted/income_statement_annual.csv` | Op Income / Revenue FY2026 |
| 115% | 2 | `/input/repo/extracted/financial_summary.json` | `"nrr": [..., 115]` |
| $860M | 2 | `/input/repo/extracted/financial_summary.json` | `"arr": [..., 860]` |
| $1.26B | 2 | `/input/repo/extracted/balance_sheet_annual.csv` | Cash & Investments, 2026-01-31: 1,259,903,000 |
| $0.2M | 2 | `/input/repo/extracted/balance_sheet_annual.csv` | Total Debt, 2026-01-31: 187,000 |

## Slide 3: What Would Change Recommendation

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 110% | 3 | `/input/repo/memo/gitlab_investment_memo.md` | Risk Assessment: "If this trend continues below 110%" |

## Slide 4: Financial Trajectory

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| $424M | 4 | `/input/repo/extracted/income_statement_annual.csv` | Total Revenue, 2023-01-31 |
| $580M | 4 | `/input/repo/extracted/income_statement_annual.csv` | Total Revenue, 2024-01-31: 579,906,000 |
| $759M | 4 | `/input/repo/extracted/income_statement_annual.csv` | Total Revenue, 2025-01-31: 759,249,000 |
| $955M | 4 | `/input/repo/extracted/income_statement_annual.csv` | Total Revenue, 2026-01-31 |
| -$84M | 4 | `/input/repo/extracted/cash_flow_annual.csv` | Free Cash Flow, 2023-01-31: -83,478,000 |
| $33M | 4 | `/input/repo/extracted/cash_flow_annual.csv` | Free Cash Flow, 2024-01-31: 33,442,000 |
| -$68M | 4 | `/input/repo/extracted/cash_flow_annual.csv` | Free Cash Flow, 2025-01-31: -67,736,000 |
| $222M | 4 | `/input/repo/extracted/cash_flow_annual.csv` | Free Cash Flow, 2026-01-31: 222,029,000 |
| 87-90% | 4 | `/input/repo/extracted/income_statement_annual.csv` | Gross Profit / Total Revenue |

## Slide 5: Competitive Position

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 2.56x | 5 | `/input/repo/extracted/competitor_data.json` | GTLB ev_revenue: 2.559 |
| 3.22x | 5 | `/input/repo/extracted/competitor_data.json` | TEAM ev_revenue: 3.215 |
| 12.39x | 5 | `/input/repo/extracted/competitor_data.json` | DDOG ev_revenue: 12.388 |
| 7.03x | 5 | Derived | Average of 8 peer EV/Revenue multiples |
| 23% | 5 | `/input/repo/extracted/competitor_data.json` | GTLB revenue_growth: 0.232 |

## Slide 6: Mispricing Thesis

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| $30.79 | 6 | `/input/repo/extracted/company_info.json` | targetMeanPrice: 30.79167 |
| $38.52 | 6 | `/input/repo/memo/gitlab_investment_memo.md` | DCF Implied Price |
| $53.25 | 6 | `/input/repo/memo/gitlab_investment_memo.md` | Peer EV/Revenue Implied Price |
| 2.6x | 6 | `/input/repo/extracted/competitor_data.json` | GTLB EV/Revenue: 2.559 |
| 7.0x | 6 | Derived | Peer average EV/Revenue |

## Slide 7: Risk Assessment

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 120% | 7 | `/input/repo/extracted/financial_summary.json` | nrr[0]: 120 |
| 115% | 7 | `/input/repo/extracted/financial_summary.json` | nrr[4]: 115 |
| 110% | 7 | `/input/repo/memo/gitlab_investment_memo.md` | Risk threshold |

## Slide 8: Bear/Base/Bull

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| $18.58 | 8 | `/input/repo/memo/gitlab_investment_memo.md` | Bear case price |
| $38.52 | 8 | `/input/repo/memo/gitlab_investment_memo.md` | Base case price |
| $88.30 | 8 | `/input/repo/memo/gitlab_investment_memo.md` | Bull case price |
| 25% | 8 | `/input/repo/memo/gitlab_investment_memo.md` | Bear probability |
| 50% | 8 | `/input/repo/memo/gitlab_investment_memo.md` | Base probability |
| 25% | 8 | `/input/repo/memo/gitlab_investment_memo.md` | Bull probability |
| $45.98 | 8 | `/input/repo/memo/gitlab_investment_memo.md` | Probability-weighted target |
| 114% | 8 | Derived | ($45.98 - $21.51) / $21.51 |

## Slide 9: DCF Bridge

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 10.5% | 9 | `/input/repo/decisions/003-valuation-methodology.md` | WACC |
| 3.0% | 9 | `/input/repo/decisions/003-valuation-methodology.md` | Terminal growth |
| 4.5% | 9 | `/input/repo/decisions/003-valuation-methodology.md` | Risk-free rate |
| 1.2 | 9 | `/input/repo/decisions/003-valuation-methodology.md` | Beta |
| 5.5% | 9 | `/input/repo/decisions/003-valuation-methodology.md` | Equity risk premium |

## Slide 10: Reasoning Trail

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 6 | 10 | `/input/repo/raw/transcripts/` | 6 transcript files |
| 3 | 10 | `/input/repo/decisions/` | 3 ADR files |
| 5 | 10 | `/input/repo/research/dead-ends.md` | 5 dead ends |

## Slide 11: Dead Ends

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 5 | 11 | `/input/repo/research/dead-ends.md` | 5 dead end sections |

## Slide 12: Confidence

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 9/10 | 12 | Derived | Revenue trajectory confidence |
| 10/10 | 12 | Derived | Balance sheet confidence |
| 5/10 | 12 | Derived | ARR/NRR confidence |
| 4/10 | 12 | Derived | AI monetization confidence |

## Slide 13: Audit Mechanism

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| 15 | 13 | This deck | Total number of slides |
| 2 min | 13 | This deck | Time to verify any claim |

## Slide 14: Reconciliation

| Number | Slide | Source File | Source Location |
|--------|-------|-------------|-----------------|
| See reconciliation.md | 14 | `/audit/reconciliation.md` | 5 spot-checked numbers |
