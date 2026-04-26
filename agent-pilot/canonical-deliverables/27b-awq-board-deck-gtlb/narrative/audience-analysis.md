# Audience Analysis: Board of Advisors

**Date:** 2025-06-18
**Author:** Investment Agent

## Who's on the Board

The audience is a board of advisors evaluating an AI investment agent system. They are:

1. **Technical** — They understand financial models, DCF analysis, and SaaS metrics. They can spot hand-waving.
2. **Skeptical** — They've seen AI systems overpromise. They want to see the reasoning, not just the conclusion.
3. **Time-constrained** — 30 minutes for the presentation, 15 minutes for Q&A. Every slide must earn its place.
4. **Audit-minded** — They want to verify claims, not just accept them. The traceability requirement is central.

## What They Care About

| Concern | How the Deck Addresses It |
|---------|--------------------------|
| **Is the recommendation sound?** | Slides 1-3: Clear recommendation with price target and thesis |
| **Can we trust the agent's reasoning?** | Slides 10-12: Full reasoning trail, dead ends, confidence assessment |
| **Are the numbers real?** | Slide 13: Self-audit mechanism with trace files |
| **What could go wrong?** | Slide 8: Prioritized risk assessment with conditions for materialization |
| **How confident should we be?** | Slide 12: Visual confidence spectrum with limitations |
| **What would change the recommendation?** | Slide 3: Explicit thesis-breakers |
| **Is the valuation methodology appropriate?** | Slide 14: ADR summary with WACC, terminal growth, comp selection rationale |

## How the Deck Addresses Each Concern

### Technical Rigor
- Every chart is reproducible from scripts in `/assets/charts/`
- Every number traces back to `/input/repo/` via `/audit/traces/`
- Valuation methodology documented in ADR-003
- Financial data sourced from yfinance (SEC-derived)

### Transparency
- Dead ends are surfaced honestly (Slide 11)
- Limitations are visualized, not hidden (Slide 12)
- The reasoning trail is a dedicated slide (Slide 10)
- Self-audit mechanism is explained (Slide 13)

### Actionability
- Clear recommendation with price target (Slide 1)
- Position sizing guidance (Slide 15)
- Catalysts and holding period (Slide 15)
- Thesis-breakers identified (Slide 3)

### Verification
- Every claim has a trace file
- Numbers are reconciled in `/audit/reconciliation.md`
- Quotes include surrounding context in `/audit/quotes.md`
- Charts are reproducible from source scripts

## Design Decisions Driven by Audience

1. **Charts over text** — Technical audience prefers data visualization to prose
2. **Traceability over polish** — Audit trail is more important than visual flair
3. **Honesty over confidence** — Surface limitations explicitly rather than bury them
4. **Reproducibility over convenience** — Every chart has a script; every number has a source
5. **Structure over surprise** — Standard board presentation structure adapted for agent evaluation
