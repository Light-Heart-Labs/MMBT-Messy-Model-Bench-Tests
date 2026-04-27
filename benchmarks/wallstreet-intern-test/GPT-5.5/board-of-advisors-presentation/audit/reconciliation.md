# Reconciliation Spot Check
Input commit: `8bb17db58bbb4201937887c6af6ee6e2b530d2fb`

| number | trace | input_path | source_chain | reconciliation |
| --- | --- | --- | --- | --- |
| $39.62 current price | T001 | /input/repo/analysis/memo_trace_table.csv:3 | raw/other/stockanalysis-yeti-market-cap.html and raw/other/stockanalysis-yeti-statistics.html -> extracted/yeti_market_data.csv | StockAnalysis market page -> extracted market data -> model Cover!B7 -> memo/deck. |
| $1.868B FY2025 revenue | T005 | /input/repo/analysis/memo_trace_table.csv:7 | raw/filings/yeti-2026-02-27-10-k-yeti-20260103.htm -> extracted/yeti_financials_annual.csv -> extracted/yeti_financials_wide.csv | SEC 10-K revenue fact -> annual/wide extracted CSV -> Model!D5 -> memo/deck. |
| 10.8% WACC | T018 | /input/repo/analysis/memo_trace_table.csv:20 | raw/other/stockanalysis-yeti-market-cap.html and raw/other/stockanalysis-yeti-statistics.html -> extracted/yeti_market_data.csv | Risk-free/ERP/beta/debt inputs -> Assumptions!B18 -> valuation/deck. |
| $41 target | T003 | /input/repo/analysis/memo_trace_table.csv:5 | model/yeti_investment_model.xlsx -> model/key-outputs.ndjson | DCF/multiple blend -> Valuation!B19 -> Cover!B6 -> memo/deck. |
| 200 bps tariff impact | T042 | /input/repo/analysis/memo_trace_table.csv:44 | raw/transcripts/yeti-q4-2025-earnings-call-transcript.pdf -> extracted/transcripts/yeti-q4-2025-earnings-call-transcript.txt | Q4 transcript line context -> trace table risk row -> risk slide. |
