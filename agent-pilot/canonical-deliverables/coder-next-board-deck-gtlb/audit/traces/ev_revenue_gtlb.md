# Trace File: EV/Revenue GitLab

**Number:** 2.56x  
**Slide:** 5, 8 (Competitive Landscape, Valuation)  
**Date:** 2025-06-18

---

## Source Path

`/input/repo/extracted/competitor_data.json`

## File Details

- **File:** competitor_data.json
- **Key:** GTLB.ev_revenue
- **Value:** 2.559
- **Formatted:** 2.56x

## Data Provenance

1. **Source:** yfinance API
2. **yfinance Source:** Market data, financial statements
3. **Market Data:** Nasdaq GS (GTLB)
4. **Market Cap:** $3.66B (from company_info.json)
5. **Enterprise Value:** Calculated as Market Cap + Debt - Cash

## Verification Steps

1. Open `/input/repo/extracted/competitor_data.json`
2. Find key "GTLB"
3. Find sub-key "ev_revenue"
4. Value: 2.559
5. Round to 2 decimal places: 2.56x

## Notes

- EV/Revenue = Enterprise Value / Revenue
- Enterprise Value = Market Cap + Total Debt - Cash
- GitLab's EV/Revenue is significantly below peer average (6.71x)

## Related Files

- `/input/repo/memo/gitlab_investment_memo.md` - Shows 2.56x in "Competitive Analysis"
- `/input/repo/extracted/competitor_data.json` - Full competitor data
- `/input/repo/extracted/company_info.json` - Market cap and cash data

## Traceability Chain

```
Deck Slide 5 → 2.56x → competitor_data.json → yfinance → market data
```

## Verification Time

- **Time to verify:** <2 minutes
- **Steps:** 4 simple steps
- **Difficulty:** Easy
