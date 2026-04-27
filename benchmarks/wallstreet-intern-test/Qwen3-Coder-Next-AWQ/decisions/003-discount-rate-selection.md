# ADR 003: Discount Rate (WACC) Selection

**Date**: 2024-10-02  
**Status**: Approved

## WACC Components

1. **Cost of Equity (CAPM)**:
   - Risk-free rate: 4.5% (10-year Treasury)
   - Market risk premium: 5.5%
   - Beta: 0.99 (DocuSign)
   - Cost of equity: 4.5% + 0.99 × 5.5% = 9.95%

2. **Cost of Debt**: 4.0% (DocuSign debt yield)

3. **Capital Structure**:
   - Equity: 85% (Market cap $9B / (Market cap + Debt $0.2B))
   - Debt: 15%

4. **Tax Rate**: 21% (federal)

## Calculated WACC

WACC = (0.85 × 9.95%) + (0.15 × 4.0% × (1 - 0.21)) = 8.46% + 0.47% = **8.93%**

## Decision

Rounded to **9.0% WACC** for the following reasons:

- **Simplicity**: 9% is a clean number for modeling
- **Margin of safety**: Slightly higher than calculated 8.93%
- **Industry comparison**: SaaS companies typically use 8-10% WACC
- **Risk adjustment**: DocuSign's working capital volatility warrants slight premium

## Alternative Considered

**8.0% WACC** would imply higher valuation ($115/share) but doesn't adequately compensate for:
- Working capital management risks (current ratio 0.73)
- Integration risks from Lexion acquisition
- Competitive pressures in agreement automation space

## Exit Criteria

If DocuSign's beta increases above 1.2 or interest rates rise significantly, revisit WACC assumption.
