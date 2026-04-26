# Storyboard: GitLab (GTLB) Board Presentation

**Date:** 2025-06-18
**Author:** Investment Agent
**Status:** DRAFT — committed before any slide construction

## Narrative Arc

The board is skeptical. They've read the memo. They want to know: *Can we trust this agent's reasoning?* The deck must answer that question while also making the investment case.

**Core tension:** The agent is a non-human analyst with real limitations (no SEC filing access, no customer calls, no live earnings participation). The deck must be honest about these gaps while demonstrating that the reasoning trail is rigorous and auditable.

**Narrative structure:** Lead with the recommendation → show the thesis → walk through the evidence → surface the reasoning process → end with limitations and how to verify.

## Slide-by-Slide Plan (18 slides)

### Section 1: The Recommendation (Slides 1-3)

**Slide 1: Title & Recommendation**
- GitLab Inc. (GTLB) — BUY
- Price target: $42.00 (95% upside from $21.51)
- Probability-weighted target: $45.98
- One-line thesis: "The market is underpricing GitLab's AI monetization, operating leverage, and balance sheet strength"

**Slide 2: The Thesis — In the Agent's Own Words**
- 5 pillars from the memo, quoted directly
- Large TAM, proven growth engine, path to profitability, strong balance sheet, what the market is missing
- Source: `/input/repo/memo/gitlab_investment_memo.md`

**Slide 3: What Would Change Our Mind**
- 2-3 thesis-breakers: NRR below 110%, GitHub captures full DevOps workflow, macro recession cutting enterprise spend
- Shows intellectual honesty — we know what would invalidate the thesis

### Section 2: The Evidence (Slides 4-8)

**Slide 4: Financial Trajectory — Revenue & Margins**
- Historical revenue: $424M → $955M (FY2023-FY2026)
- Operating margin trajectory: -50% → -7%
- Inflection points: FCF turns positive FY2024, margin improvement accelerates
- Chart: Dual-axis (revenue bars + margin line)

**Slide 5: SaaS Metrics — The Engine**
- ARR: $300M → $860M
- NRR: 120% → 115% (declining but still strong)
- Gross margin: stable 87-90%
- Deferred revenue: $572M (visibility)
- Chart: ARR growth with NRR overlay

**Slide 6: Competitive Position**
- Scatter plot: Revenue growth vs. EV/Revenue for comp set
- GitLab positioned: high growth, low multiple = mispricing
- Why these comps: ADR-002 rationale
- Chart: Growth-vs-multiple scatter

**Slide 7: The Mispricing Thesis**
- Current EV/Revenue: 2.56x vs. peer average 7.03x
- DCF base case: $38.52 vs. current $21.51
- Three factors the market is missing: AI monetization, operating leverage, balance sheet
- Visual: Gap between current price and valuation anchors

**Slide 8: Risk Assessment — Prioritized**
- Heat map: Probability vs. Impact for each risk
- NRR decline (high/high), GitHub competition (med/high), macro (med/high), AI monetization failure (med/med), open-source cannibalization (low/high), key person (low/med)
- What would have to be true for each to materialize

### Section 3: The Reasoning (Slides 9-12)

**Slide 9: Bear/Base/Bull — Probability-Weighted Distribution**
- Not three bullet points — a proper distribution visualization
- Bear (25%): $18.58, Base (50%): $38.52, Bull (25%): $88.30
- Weighted: $45.98
- Chart: Probability distribution with current price marker

**Slide 10: The Reasoning Trail — How We Got Here**
- Dependency graph: filings read → data extracted → analysis performed → decisions made → conclusion reached
- Shows the actual decision process, not a sanitized version
- Source: `/input/repo/decisions/` and commit history

**Slide 11: Dead Ends — What We Investigated and Rejected**
- SEC filing downloads (blocked by 403)
- IR website (DNS failure)
- PRNewswire (404)
- Wrong CIK initially
- Earnings call audio (unavailable)
- Shows the agent's work, not just the wins

**Slide 12: Confidence & Limitations — Visual**
- What we're confident about (revenue trajectory, gross margins, balance sheet, SaaS model)
- What we're estimating (ARR/NRR, AI monetization, competitive dynamics)
- What a human would do differently (5 items from memo)
- Visual: Confidence meter / spectrum

### Section 4: Verification (Slides 13-14)

**Slide 13: How to Audit This Deck**
- Self-audit slide: how a board member can clone the repo, pick any claim, and trace it
- Walkthrough: pick a number → find trace file → follow to source in input repo
- This is the most important slide for a skeptical technical board

**Slide 14: Design & Methodology Decisions**
- ADR summary: why DCF + EV/Revenue, why these comps, why this WACC
- Color palette rationale, chart conventions
- Shows that every choice was deliberate

### Section 5: Close (Slides 15-16)

**Slide 15: Recommendation & Next Steps**
- BUY, $42.00 target, 95% upside
- Position sizing: 2-3% of portfolio
- Catalysts: FY2027 Q1 earnings, GAAP profitability, AI expansion, M&A
- Holding period: 12 months

**Slide 16: Q&A / Appendix**
- Key numbers at a glance
- Contact / repo link for follow-up
- Disclaimer

## Alternatives Considered

1. **Start with the reasoning trail, end with recommendation** — Rejected. Board wants the answer first, then the proof.
2. **Include full financial model walkthrough** — Rejected. Too granular for a 30-min presentation. The model is in the input repo.
3. **Add customer case studies** — Rejected. No customer data available; would require fabrication.
4. **Include management quotes on every slide** — Rejected. Overkill; quotes used where they add context to specific claims.

## Audience Analysis

See `/narrative/audience-analysis.md` for detailed breakdown.
