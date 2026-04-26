# ADR-001: Color Palette Selection

**Date:** 2025-06-18
**Status:** Accepted

## Context
Need a consistent color palette for the board presentation that reinforces data meaning and maintains visual coherence across all slides.

## Decision
**Primary palette:**
- Blue (#2563EB): Revenue, primary data, GitLab-specific elements
- Green (#059669): Positive metrics, bull case, conclusion
- Red (#DC2626): Negative metrics, bear case, risk
- Purple (#7C3AED): ARR, SaaS metrics, scenario analysis
- Orange (#D97706): Warnings, ADRs, estimating category
- Gray (#64748B): Neutral text, current price, human-different category
- Background (#F8FAFC): Slide background
- Dark (#1E293B): Primary text

## Rationale
1. **Blue for revenue/GitLab** — Blue is the standard color for financial data and GitLab's brand uses a similar blue. This creates subconscious association.
2. **Green for positive/bull** — Universal convention. No need to reinvent.
3. **Red for negative/bear** — Universal convention. Consistent with financial reporting.
4. **Purple for SaaS metrics** — Purple is distinct from the revenue blue and positive/negative green/red, making ARR/NRR visually separable.
5. **Orange for warnings** — Orange signals caution without the alarm of red, appropriate for "estimating" category.
6. **Gray for neutral** — Gray doesn't compete with data colors, appropriate for structural elements.

## Alternatives Considered
- **GitLab brand colors** — Rejected. The deck is about analysis, not brand promotion. Using GitLab's exact colors would blur the line between analysis and marketing.
- **Diverging colormap** — Rejected. The data has a natural zero point (current price), making sequential colormaps more appropriate for price distributions.
- **Monochrome with accent** — Rejected. Too many data series require color differentiation for clarity.
