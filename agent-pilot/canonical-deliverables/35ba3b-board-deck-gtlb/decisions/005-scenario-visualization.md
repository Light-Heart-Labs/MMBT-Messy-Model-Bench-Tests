# ADR-005: Scenario Visualization — Distribution Over Bullet Points

**Date:** 2026-04-26
**Status:** Accepted

## Context
The bear/base/bull scenarios from the memo are currently presented as three bullet points with probabilities. The deck needs to visualize these as a probability-weighted distribution, not three bullet points.

## Decision
**Show the price target as a probability distribution (histogram + CDF overlay), not three bullet points.**

## Rationale
1. **Bullet points hide uncertainty** — Three bullets ("Bear: $18.58, Base: $38.52, Bull: $88.30") make the valuation look like three discrete outcomes. In reality, the distribution is continuous.
2. **Distribution shows the full picture** — A histogram with the three scenarios marked shows the shape of uncertainty: skewed right (bull case has more upside than bear case has downside).
3. **Probability-weighted** — The expected value ($45.98) is shown as a vertical line on the distribution. This makes it clear that the probability-weighted target is higher than the 12-month target ($42).
4. **Board can see the asymmetry** — The distribution shows that the upside (to $88.30) is much larger than the downside (to $18.58). This is the core of the risk/reward argument.

## Alternatives Considered
- **Three bullet points:** Rejected — hides uncertainty, doesn't show asymmetry.
- **Tornado diagram:** Rejected — shows sensitivity to individual variables, not the overall distribution.
- **Box plot:** Rejected — doesn't show the probability weights clearly.
- **Monte Carlo histogram:** Rejected — too complex for a board presentation. The three-scenario distribution is sufficient.

## Consequences
- The scenario visualization is a histogram with three bars (bear/base/bull) and a CDF overlay.
- The expected value ($45.98) is shown as a vertical line.
- The 12-month target ($42) is shown as a separate vertical line for comparison.
