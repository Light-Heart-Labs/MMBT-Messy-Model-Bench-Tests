# Questions Log

| Date | Question | Resolution | Evidence |
| --- | --- | --- | --- |
| 2026-04-27 | Which company should be selected under the $1B-$10B market-cap constraint? | Selected YETI Holdings after confirming a roughly $3.0B market cap and accessible SEC/company materials. | ADR 0001; `extracted/yeti_market_data.csv`; `sources.md`. |
| 2026-04-27 | Are transcript PDFs accessible and line-citable? | Yes. Company-hosted transcript PDFs for Q4 2024 and Q1-Q4 2025 were downloaded and converted into line-numbered text files. | `raw/transcripts/`; `extracted/transcript_line_index.csv`; `extracted/transcripts/`. |
| 2026-04-27 | What tag should be used for cash in the model? | YETI's recent filings use `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`, not only `CashAndCashEquivalentsAtCarryingValue`. | `extracted/extract_financials.py`; `extracted/yeti_financials_wide.csv`. |
| 2026-04-27 | How should DTC, wholesale, and international sales be traced? | Used the 2025 10-K Note 3 sales table parsed into `extracted/yeti_sales_breakdown.csv`. | `raw/filings/yeti-2026-02-27-10-k-yeti-20260103.htm`; `extracted/filings/yeti-2025-10k-sales-breakdown-table.txt`. |
| 2026-04-27 | Which peers should anchor valuation context? | Used GOLF, MAT, and NWL as the core peer context; kept DTC as a checked but excluded distressed data point. | ADR 0003; `extracted/peer_valuation.csv`; `analysis/competitive_analysis.md`. |
| 2026-04-27 | What discount rate is reasonable? | Used 10.8% WACC from a blended beta, current 10-year Treasury, Kroll ERP, after-tax debt cost, and market weights. | ADR 0004; `model/yeti_investment_model.xlsx` Assumptions tab. |
| 2026-04-27 | Is the sell-side missing a material upside angle? | No clear miss found. Consensus appears above management-guide-derived base assumptions, while the market price discounts risk. | ADR 0006; `analysis/sell_side_gap.md`. |
