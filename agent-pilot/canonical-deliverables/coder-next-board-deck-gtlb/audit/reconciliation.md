# Number Reconciliation

**Date:** June 18, 2025  
**Purpose:** Spot-check 5 random numbers from the deck to verify accuracy

---

## Reconciliation Methodology

1. Pick 5 random numbers from the deck
2. Trace each number to its source
3. Verify the number matches the source
4. Document any discrepancies

---

## Reconciliation #1: Revenue FY2026

**Number from Deck:** $955M  
**Source:** `/input/repo/extracted/income_statement_annual.csv`  
**Verification:**
- File: income_statement_annual.csv
- Row: Total Revenue
- Column: 2026-01-31
- Value: 955224000.0
- Formatted: $955.2M

**Discrepancy:** None (rounded to $955M in deck)

**Conclusion:** ✓ Verified

---

## Reconciliation #2: ARR FY2026

**Number from Deck:** $860M  
**Source:** `/input/repo/extracted/financial_summary.json`  
**Verification:**
- File: financial_summary.json
- Key: arr[4]
- Value: 860
- Formatted: $860M

**Discrepancy:** None

**Conclusion:** ✓ Verified

---

## Reconciliation #3: NRR FY2026

**Number from Deck:** 115%  
**Source:** `/input/repo/extracted/financial_summary.json`  
**Verification:**
- File: financial_summary.json
- Key: nrr[4]
- Value: 115
- Formatted: 115%

**Discrepancy:** None

**Conclusion:** ✓ Verified

---

## Reconciliation #4: Cash & Investments FY2026

**Number from Deck:** $1.26B  
**Source:** `/input/repo/extracted/balance_sheet_annual.csv`  
**Verification:**
- File: balance_sheet_annual.csv
- Row: Cash Cash Equivalents And Short Term Investments
- Column: 2026-01-31
- Value: 1259903000.0
- Formatted: $1,259.9M ≈ $1.26B

**Discrepancy:** None (rounded to $1.26B in deck)

**Conclusion:** ✓ Verified

---

## Reconciliation #5: EV/Revenue GitLab

**Number from Deck:** 2.56x  
**Source:** `/input/repo/extracted/competitor_data.json`  
**Verification:**
- File: competitor_data.json
- Key: GTLB.ev_revenue
- Value: 2.559
- Formatted: 2.56x

**Discrepancy:** None (rounded to 2.56x in deck)

**Conclusion:** ✓ Verified

---

## Summary

| # | Number | Source | Verified | Discrepancy |
|---|--------|--------|----------|-------------|
| 1 | $955M | income_statement_annual.csv | ✓ | None |
| 2 | $860M | financial_summary.json | ✓ | None |
| 3 | 115% | financial_summary.json | ✓ | None |
| 4 | $1.26B | balance_sheet_annual.csv | ✓ | None |
| 5 | 2.56x | competitor_data.json | ✓ | None |

**Total Verified:** 5/5  
**Discrepancies:** 0

---

## Notes

1. All spot-checked numbers are verified and accurate
2. Minor rounding differences are expected (e.g., $955.2M → $955M)
3. Trace files in `/audit/traces/` provide more detail for each number
4. Full source tracking is in `/audit/numbers.md`

---

## Verification Time

- **Time to verify all 5 numbers:** <10 minutes
- **Steps per number:** 3-4 simple steps
- **Difficulty:** Easy
