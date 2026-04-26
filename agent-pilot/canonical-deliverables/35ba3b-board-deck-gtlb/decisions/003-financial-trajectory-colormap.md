# ADR-003: Financial Trajectory Chart — Sequential Colormap Over Diverging

**Date:** 2026-04-26
**Status:** Accepted

## Context
The financial trajectory chart shows revenue, operating margin, and FCF over time. The question is whether to use a sequential colormap (light to dark) or a diverging colormap (red-blue around zero).

## Decision
**Use a sequential colormap (light to dark teal) for the financial trajectory.**

## Rationale
1. **Natural zero point** — The data has a natural reference point at the current price ($21.51) and current year (FY2026). We're showing improvement over time, not deviation from a mean.
2. **Narrative of improvement** — A sequential colormap reinforces the story of "getting better": revenue growing, margins improving, FCF turning positive.
3. **Diverging would mislead** — A diverging colormap implies symmetric distribution around zero, which doesn't apply to revenue growth or margin improvement.
4. **Consistency with scenario colors** — The bear/base/bull scenarios use red/blue/green. The financial trajectory uses teal to distinguish historical/projected data from scenario analysis.

## Alternatives Considered
- **Diverging colormap (red-blue):** Rejected — implies symmetric distribution around zero, which doesn't apply.
- **Multi-color (green for positive, red for negative):** Rejected — too busy, hard to read at presentation size.
- **Monochrome:** Rejected — less distinctive, doesn't reinforce the GitLab brand color.

## Consequences
- All financial trajectory charts use sequential teal.
- The colormap is documented in the chart script.
- Board members can distinguish trajectory data from scenario data by color.
