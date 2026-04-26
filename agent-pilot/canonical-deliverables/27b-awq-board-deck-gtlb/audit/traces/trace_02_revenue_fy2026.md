# Trace: Revenue FY2026 = $955M

**Slide:** 4 (Financial Trajectory)
**Claim:** "Revenue grew to $955M in FY2026"

**Source Chain:**
1. Primary source: `/input/repo/extracted/income_statement_annual.csv`
   - Row: "Total Revenue"
   - Column: "2026-01-31"
   - Value: 955224000.0 (in dollars)
2. Secondary: `/input/repo/extracted/financial_summary.json`
   - Field: `revenue[4]` = 955.224 (in millions)
3. Tertiary: `/input/repo/memo/gitlab_investment_memo.md`
   - Financial Summary table: Revenue FY2026 = $955M

**Calculation:**
- 955,224,000 / 1,000,000 = $955.2M
- Rounded to $955M for presentation

**Verification Steps:**
1. Open `/input/repo/extracted/income_statement_annual.csv`
2. Find row "Total Revenue", column "2026-01-31"
3. Value: 955224000.0 → $955.2M → $955M ✓
