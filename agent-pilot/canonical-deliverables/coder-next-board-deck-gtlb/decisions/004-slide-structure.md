# ADR-004: Slide Structure for Board Presentation

**Date:** 2025-06-18  
**Status:** Accepted

## Context
Need to create a 15-25 slide presentation for a technical, skeptical board of advisors. The audience wants to evaluate the agent's reasoning, not just rubber-stamp a stock pick.

## Requirements
1. Lead with the recommendation
2. Show the reasoning, not just the conclusion
3. Include a visualization of the agent's decision process
4. Surface dead ends honestly
5. Include a confidence visualization
6. One slide must audit itself (show how to verify the deck)
7. Charts should be the visual centerpiece
8. Every number must be traceable to source

## Alternatives Considered

### Alternative 1: Problem-Solution-Value (Startup Pitch Style)
- **Structure:** Problem → Solution → Market → Traction → Team → Financials → Investment Thesis → Recommendation
- **Why Rejected:** Too startup-focused; board doesn't need "pitch" format; hides recommendation until slide 8

### Alternative 2: Deep-Dive Financial Model First
- **Structure:** Financial Model → Historical Performance → Projections → DCF → EV/Revenue → Scenario Analysis → Investment Thesis → Risk Assessment → Recommendation
- **Why Rejected:** Leads with technical details; board may lose interest; doesn't tell a compelling story

### Alternative 3: Question-Driven Narrative
- **Structure:** Is GitLab undervalued? → Why? → How do we know? → What could go wrong? → How do we verify?
- **Why Rejected:** Too abstract; lacks concrete data early; doesn't lead with recommendation

### Alternative 4: Competitive-First Approach
- **Structure:** Competitive Landscape → GitLab's Position → Competitive Advantages → Market Opportunity → Financials → Valuation → Recommendation
- **Why Rejected:** Doesn't show agent's reasoning process; doesn't show dead ends; doesn't emphasize verification mechanism

### Alternative 5: Timeline-Driven Narrative
- **Structure:** Company History → Recent Performance → Current Position → Future Projections → Valuation → Recommendation
- **Why Rejected:** Too chronological; doesn't highlight key insights; doesn't show agent's reasoning process

### Alternative 6: Risk-First Approach
- **Structure:** Key Risks → Mitigation Strategies → Investment Thesis → Financials → Valuation → Recommendation
- **Why Rejected:** Too negative; sets wrong tone; doesn't lead with recommendation

## Decision

**Selected Structure: Recommendation-First with Reasoning Trail**

### Slide-by-Slide Structure

| Slide | Title | Purpose | Key Content |
|-------|-------|---------|-------------|
| 1 | Title Slide | Establish recommendation | BUY, $42.00 target, $21.51 current |
| 2 | Recommendation Summary | Reinforce recommendation | Probability-weighted $45.98, 114% upside |
| 3 | Investment Thesis | Core argument | 5 key points from memo |
| 4 | Financial Trajectory | Data behind thesis | Historical + projected; inflection points |
| 5 | Competitive Landscape | Market position | 8 comparable companies |
| 6 | Competitive Advantages | Why GitLab wins | Full-stack, open-core, single app, AI |
| 7 | What the Market Is Missing | Mispricing | AI monetization, operating leverage, ARR |
| 8 | Valuation Approach | How we got to price | DCF + EV/Revenue; methodology |
| 9 | Risk Assessment | Downside consideration | Prioritized risks; what would have to be true |
| 10 | Bear/Base/Bull Scenarios | Range of outcomes | Probability-weighted visualization |
| 11 | Agent's Decision Process | How we got here | Dependency graph: filings → analysis → conclusion |
| 12 | Dead Ends | What we ruled out | 3-4 dead ends; why they failed; how we adapted |
| 13 | How to Audit This Deck | Verification mechanism | Trace files; source paths; reconciliation |
| 14 | Confidence and Limitations | What we know vs. estimate | Confidence levels; limitations; human analyst differences |
| 15 | Recommendation Recap | Next steps | Position sizing, catalysts, holding period |
| 16 | Q&A | Open floor | Contact info |

### Timing Breakdown

| Section | Slides | Time |
|---------|--------|------|
| Opening | 2 | 5 min |
| Thesis | 2 | 5 min |
| Competitive | 2 | 4 min |
| Mispricing | 2 | 4 min |
| Risk | 2 | 4 min |
| Reasoning | 2 | 5 min |
| Verification | 2 | 3 min |
| Closing | 2 | 2 min |
| **Total** | **16** | **30 min** + 15 min Q&A |

## Rationale

### Why This Structure Works

1. **Leads with conclusion** - Board members are busy; they need to know the recommendation first
2. **Shows reasoning** - Technical board wants to evaluate the process, not just the result
3. **Demonstrates thoroughness** - Shows dead ends and how we adapted
4. **Enables verification** - Every claim is traceable to source
5. **Balances data and narrative** - Charts tell the story; text provides context

### Key Differentiators

1. **Slide 1: Recommendation** - What we think
2. **Slide 3: Thesis** - Why we think it
3. **Slide 11: Reasoning Trail** - How we got there
4. **Slide 12: Dead Ends** - What we ruled out
5. **Slide 13: Verification** - How to check our work

This structure is designed for a skeptical, technical audience that wants to evaluate the reasoning, not just rubber-stamp a recommendation.

## Implementation

### Tools
- Python with `python-pptx` for PowerPoint generation
- Matplotlib for charts
- Plotly for interactive charts (optional)

### Design Principles
1. **Charts as centerpiece** - Every slide should have at least one chart
2. **Color consistency** - Use same colors for scenarios (bear=red, base=green, bull=blue)
3. **Data density** - More data per slide, less text
4. **Traceability** - Every number should have a source path visible

### Verification Mechanism
- Every number has a trace file in `/audit/traces/`
- Every quote has a source path in `/audit/quotes.md`
- Every number has a source in `/audit/numbers.md`
- 5 random numbers are reconciled in `/audit/reconciliation.md`

## Limitations

1. **16 slides is tight** - May need to combine some slides if time is limited
2. **Charts take time** - Need to create reproducible charts with scripts
3. **Trace files are manual** - Need to create trace files for every number
4. **Verification mechanism is new** - May need to refine based on board feedback

## Next Steps

1. Create trace files for every number
2. Build financial trajectory chart
3. Build competitive landscape chart
4. Build scenario analysis visualization
5. Create reasoning trail diagram
6. Document dead ends
7. Create audit documentation
8. Generate PowerPoint deck
9. Export to PDF

## Approval

**Approved by:** Board Presentation Agent  
**Date:** 2025-06-18  
**Status:** Accepted
