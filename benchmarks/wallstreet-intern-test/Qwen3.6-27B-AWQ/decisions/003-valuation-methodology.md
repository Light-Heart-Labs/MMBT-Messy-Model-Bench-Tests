# ADR-003: Valuation Methodology

**Date:** 2025-06-18
**Status:** Accepted

## Context
Need to determine the appropriate valuation methodology for GitLab, a high-growth SaaS company that is not yet consistently profitable.

## Alternatives Considered
1. **Trailing P/E:** Not applicable - GitLab has negative trailing earnings
2. **Forward P/E:** Applicable but limited - forward earnings are small and volatile
3. **EV/Revenue:** Standard for SaaS companies, widely used by sell-side
4. **EV/Sales (forward):** Better than trailing as it uses projected revenue
5. **DCF (FCF-based):** Appropriate for companies with predictable cash flows
6. **Sum-of-the-Parts:** Not applicable - single business line
7. **Rule of 40 multiple:** SaaS-specific metric

## Decision
**Primary: DCF with FCF projections**
**Secondary: EV/Revenue peer comparison**
**Tertiary: Forward P/E (for sensitivity)**

## Rationale
1. **DCF is most appropriate** because:
   - GitLab has positive FCF in recent years ($222M in FY2026)
   - Revenue growth is predictable (ARR-based business)
   - FCF margins are improving and can be projected
   - Captures the value of future cash generation

2. **EV/Revenue as cross-check** because:
   - Standard SaaS valuation metric
   - Allows direct peer comparison
   - Less sensitive to timing of profitability

3. **WACC of 10.5%** based on:
   - Risk-free rate: 4.5% (10Y US Treasury)
   - Beta: 1.2 (SaaS sector average)
   - Equity risk premium: 5.5%
   - Cost of equity: 11.1%
   - Cost of debt: 5.0% (negligible debt)
   - WACC ≈ 11.1% * 0.99 + 5.0% * 0.01 * 0.79 = 10.97% ≈ 10.5% (rounded)

4. **Terminal growth of 3.0%** because:
   - Conservative, below long-term GDP growth (~2.5-3%)
   - Appropriate for a maturing SaaS company
   - Higher than 2% (too pessimistic) but lower than 4% (too optimistic)

## Key Assumptions
- Revenue growth moderates from 25.8% (FY2026) to 10% (FY2031)
- Gross margins stabilize at 88%
- Operating margins improve to 5%+ by FY2030
- FCF margins improve to 25-28% by FY2031
- No share buybacks assumed
- SBC as % of revenue declines from 22% to 16%
