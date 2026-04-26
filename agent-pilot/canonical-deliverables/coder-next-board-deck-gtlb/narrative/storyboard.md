# GitLab Inc. (GTLB) Board of Advisors Presentation - Storyboard

**Date:** June 18, 2025  
**Audience:** Board of Advisors (Technical, Skeptical)  
**Goal:** Demonstrate agent reasoning and provide a verifiable investment recommendation

---

## Narrative Arc

### 1. Opening (5 minutes)
- **Slide 1: Title Slide** - Recommendation, price target, current price
- **Slide 2: Recommendation Summary** - BUY with $42.00 target (95% upside), probability-weighted $45.98

### 2. The Thesis (5 minutes)
- **Slide 3: Investment Thesis in Agent's Words** - Direct quotes from memo, 5 key points
- **Slide 4: Financial Trajectory** - Historical + projected, inflection points called out

### 3. Competitive Position (4 minutes)
- **Slide 5: Competitive Landscape** - 8 comparable companies, why this set
- **Slide 6: Competitive Advantages** - Full-stack, open-core, single app, AI integration

### 4. The Mispricing (4 minutes)
- **Slide 7: What the Market Is Missing** - AI monetization, operating leverage, ARR quality
- **Slide 8: Valuation Approach** - DCF + EV/Revenue, why both, methodology

### 5. Risk Assessment (4 minutes)
- **Slide 9: Risk Prioritization** - High/Medium/Low probability/impact matrix
- **Slide 10: Bear/Base/Bull Scenarios** - Probability-weighted visualization

### 6. The Reasoning Trail (5 minutes)
- **Slide 11: Agent's Decision Process** - Dependency graph: filings → analysis → conclusion
- **Slide 12: Dead Ends** - What didn't work, why, and how we adapted

### 7. Verification & Confidence (3 minutes)
- **Slide 13: How to Audit This Deck** - Self-audit mechanism, trace files, source paths
- **Slide 14: Confidence and Limitations** - What we're confident about vs. what we're estimating

### 8. Closing (2 minutes)
- **Slide 15: Recommendation Recap** - Position sizing, catalysts, holding period
- **Slide 16: Q&A** - Open floor for questions

---

## Key Design Decisions

### Why This Order?
1. **Lead with recommendation** - Board members are busy; they need to know the conclusion first
2. **Thesis before data** - Provides context for why we're showing specific numbers
3. **Competitive before valuation** - Understanding the market position informs valuation multiples
4. **Reasoning trail before verification** - Shows how we got here before showing how to verify
5. **Dead ends before confidence** - Demonstrates thoroughness by showing what we ruled out

### Why Visuals Over Text?
- Board has read the memo; this is for discussion, not redelivery
- Charts should be the visual centerpiece
- Every number must be traceable to source

### Why Show Dead Ends?
- Technical board wants to evaluate reasoning, not just results
- Shows we considered alternatives and made deliberate choices
- Builds credibility through transparency

---

## Timing Breakdown

| Section | Slides | Time | Q&A |
|---------|--------|------|-----|
| Opening | 2 | 5 min | - |
| Thesis | 2 | 5 min | - |
| Competitive | 2 | 4 min | - |
| Mispricing | 2 | 4 min | - |
| Risk | 2 | 4 min | - |
| Reasoning | 2 | 5 min | - |
| Verification | 2 | 3 min | - |
| Closing | 2 | 2 min | 15 min |
| **Total** | **16** | **30 min** | **15 min** |

---

## Source Material Mapping

| Slide | Memo Section | Data Source |
|-------|--------------|-------------|
| 1 | Title | Memo header |
| 2 | Executive Summary | Memo header |
| 3 | Investment Thesis | Memo "Investment Thesis" section |
| 4 | Financial Summary | Memo "Financial Summary" + extracted CSV |
| 5 | Competitive Analysis | Memo "Competitive Analysis" + competitor_data.json |
| 6 | Competitive Advantages | Memo "Competitive Advantages" section |
| 7 | Investment Thesis (continued) | Memo "What the Market Is Missing" |
| 8 | Valuation | Memo "Valuation" section + model |
| 9 | Risk Assessment | Memo "Risk Assessment" section |
| 10 | Scenario Analysis | Memo "Scenario Analysis" + model |
| 11 | Analysis Summary | analysis/analysis_summary.md + decisions/ |
| 12 | Dead Ends | research/dead-ends.md |
| 13 | Limitations | Memo "Confidence and Limitations" |
| 14 | Limitations (continued) | Memo "Limitations" + research/questions.md |
| 15 | Recommendation | Memo "Recommendation" section |
| 16 | Q&A | - |

---

## Traceability Strategy

Every claim on every slide will have:
1. **Trace file** in `/audit/traces/` pointing to input repo
2. **Source path** in `/audit/numbers.md` and `/audit/quotes.md`
3. **Reconciliation** of 5 random numbers in `/audit/reconciliation.md`

This ensures a board member can:
- Pick any number on any slide
- Click through to the trace
- Find the original source in <2 minutes
