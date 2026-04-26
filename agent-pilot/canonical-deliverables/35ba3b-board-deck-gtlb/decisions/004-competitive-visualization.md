# ADR-004: Competitive Position — Scatter Plot Over Pie Chart

**Date:** 2026-04-26
**Status:** Accepted

## Context
The competitive position slide needs to show GitLab's position relative to competitors. The question is whether to use a pie chart (market share) or a scatter plot (growth vs. margin).

## Decision
**Use a scatter plot with revenue growth on the x-axis and operating margin on the y-axis.**

## Rationale
1. **Pie chart obscures the thesis** — A pie chart of market share would show GitLab as a small slice, which reinforces the narrative that GitLab is a niche player. But the thesis is that GitLab is *undervalued* relative to its growth and competitive position.
2. **Scatter reveals the mispricing** — A scatter plot of growth vs. margin shows GitLab as an outlier: high growth (23%) with improving margins (-7.4%) at a low EV/Revenue multiple (2.6x). This is the core of the investment case.
3. **Board can see the comparison** — Each competitor is a point on the scatter. GitLab's position relative to peers is immediately visible.
4. **Consistent with the mispricing thesis** — The scatter plot visually demonstrates that GitLab is priced like a low-growth, low-margin company when it's actually high-growth with improving margins.

## Alternatives Considered
- **Pie chart (market share):** Rejected — obscures the thesis, shows GitLab as small.
- **Bar chart (EV/Revenue comparison):** Rejected — only shows one dimension. The scatter shows growth AND margin.
- **Radar chart:** Rejected — hard to read at presentation size, too many dimensions.

## Consequences
- The scatter plot is the centerpiece of the competitive position slide.
- Each competitor gets a consistent color across all slides.
- GitLab is highlighted with a larger marker and label.
