# Extracted Data

Run the extractors from the repository root:

```powershell
python extracted\extract_transcripts.py
python extracted\extract_financials.py
```

Key outputs:

- `yeti_financials_annual.csv`: long-form SEC XBRL facts with source tags and filing paths.
- `yeti_financials_wide.csv`: model-ready historical financials.
- `yeti_sales_breakdown.csv`: product/channel/geography sales from the FY2025 Form 10-K.
- `transcript_line_index.csv`: transcript text with source PDF, page, and line number.
- `yeti_market_data.csv`, `peer_valuation.csv`, and `yeti_2026_guidance.csv`: valuation and assumption inputs.

