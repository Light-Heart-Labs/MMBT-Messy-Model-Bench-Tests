# ADR-002: Chart Conventions

**Date:** 2025-06-18
**Status:** Accepted

## Context
Need consistent chart conventions across all slides to ensure the board can read any chart without relearning conventions.

## Decision
1. **Dual-axis charts** — Revenue on left axis (bars), margins on right axis (line). Consistent across all financial trajectory charts.
2. **Scatter plots for competitive analysis** — Growth on X-axis, valuation multiple on Y-axis. Bubble size = market cap.
3. **Probability distributions for scenarios** — Not bullet points. Actual density curves with current price and weighted target markers.
4. **Heat maps for risk** — Probability on X-axis, impact on Y-axis. Bubble size = combined risk score.
5. **Dependency graphs for reasoning** — Top-down flow: data sources → extraction → analysis → decisions → conclusion.
6. **All charts have source annotations** — Every chart includes a small text noting the source file in the input repo.

## Rationale
1. **Dual-axis** — Standard financial convention. Board members expect this.
2. **Scatter for comps** — Most informative way to show relative positioning. Pie charts would obscure the growth dimension.
3. **Distributions for scenarios** — A single number ($42.00) hides the uncertainty. A distribution shows the range and probability.
4. **Heat maps for risk** — Two-dimensional risk assessment is more informative than a list.
5. **Dependency graphs** — Shows the actual reasoning process, not a sanitized version.
6. **Source annotations** — Supports the auditability requirement.

## Alternatives Considered
- **Waterfall charts for revenue** — Rejected. Bar charts are more familiar to the board.
- **Radar charts for competitive analysis** — Rejected. Radar charts are hard to read and don't show the growth-vs-valuation tradeoff clearly.
- **Box plots for scenarios** — Rejected. Box plots don't show the probability weighting clearly.
- **Sankey diagrams for reasoning** — Rejected. Sankey diagrams are better for flow volumes, not decision dependencies.
