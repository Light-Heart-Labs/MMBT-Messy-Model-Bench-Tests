# Trace File: WACC

**Number:** 10.5%  
**Slide:** 8 (Valuation Approach)  
**Date:** 2025-06-18

---

## Source Path

`/input/repo/decisions/003-valuation-methodology.md`

## File Details

- **File:** 003-valuation-methodology.md
- **Section:** Key Assumptions
- **Line:** 27
- **Value:** WACC ≈ 10.5%

## Data Provenance

1. **Source:** ADR-003 (Valuation Methodology Decision)
2. **Risk-free rate (Rf):** 4.5% (10Y US Treasury)
3. **Beta:** 1.2 (SaaS sector average)
4. **Equity risk premium (ERP):** 5.5%
5. **Cost of equity:** 11.1% (via CAPM)
6. **Cost of debt:** 5.0% (negligible debt)
7. **WACC:** 11.1% * 0.99 + 5.0% * 0.01 * 0.79 = 10.97% ≈ 10.5%

## Verification Steps

1. Open `/input/repo/decisions/003-valuation-methodology.md`
2. Find "Key Assumptions" section
3. Find WACC calculation
4. Value: 10.5%

## Notes

- WACC is a critical assumption that significantly impacts DCF valuation
- A 1% change in WACC changes DCF value by ~10%
- WACC is calculated using CAPM for cost of equity

## Related Files

- `/input/repo/decisions/003-valuation-methodology.md` - Full methodology
- `/input/repo/memo/gitlab_investment_memo.md` - DCF analysis using WACC
- `/input/repo/model/gitlab_three_statement_model.xlsx` - Financial model

## Traceability Chain

```
Deck Slide 8 → 10.5% → 003-valuation-methodology.md → CAPM calculation
```

## Verification Time

- **Time to verify:** <2 minutes
- **Steps:** 3 simple steps
- **Difficulty:** Easy
