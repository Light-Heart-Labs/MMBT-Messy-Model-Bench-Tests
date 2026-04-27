# ADR 004: Terminal Growth Rate Selection

**Date**: 2024-10-02  
**Status**: Approved

## Terminal Growth Options

1. **0%**: No long-term growth, implies company matures and stabilizes
2. **2%**: Inflation-adjusted growth, conservative but realistic
3. **3%**: Historical GDP growth, moderate growth assumption
4. **4%**: Above GDP growth, assumes continued market expansion

## Decision

Selected **3% terminal growth rate** for the following reasons:

- **Industry context**: SaaS industry average terminal growth is 2-4%
- **Market opportunity**: Agreement automation TAM is growing at 15-20% CAGR
- **Company position**: DocuSign is market leader with expansion potential
- **Sustainability**: 3% is below long-term GDP growth, making it sustainable

## Calculation Impact

- **2% terminal growth**: $98/share
- **3% terminal growth**: $105/share (selected)
- **4% terminal growth**: $112/share

## Alternative Considered

**2% terminal growth** would be appropriate for a mature, low-growth company, but DocuSign:
- Has significant expansion opportunity in IAM market
- Benefits from network effects
- Has high gross margins (82%) allowing for growth reinvestment

## Exit Criteria

If DocuSign's market share in agreement automation stagnates or competitive pressures increase, reduce terminal growth to 2%.
