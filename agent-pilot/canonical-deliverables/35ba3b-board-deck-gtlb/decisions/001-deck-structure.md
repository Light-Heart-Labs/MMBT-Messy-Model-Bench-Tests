# ADR-001: Deck Structure — Lead with Recommendation, Not Process

**Date:** 2026-04-26
**Status:** Accepted

## Context
The board has already read the investment memo. They know the recommendation is BUY at $42. The deck needs to serve a different purpose: facilitate discussion and demonstrate the agent's reasoning capability.

## Decision
**Lead with the recommendation (Slide 1), then the thesis (Slide 2), then evidence (Slides 3-9), then process (Slides 10-12), then verification (Slides 13-15).**

## Rationale
1. **Board has read the memo** — No need to build up to the recommendation. Lead with it.
2. **Discussion-oriented** — The deck is for conversation, not redelivery.
3. **Capability demonstration** — The process slides (10-12) show how the agent got there.
4. **Trust building** — The verification slides (13-15) let the board audit the work.

## Alternatives Considered
- **Chronological (data → analysis → conclusion):** Rejected — feels like a lecture.
- **Risk-first:** Rejected — frames investment defensively.
- **Competitive-first:** Rejected — secondary to financial trajectory.

## Consequences
- The deck is structured for a skeptical technical audience.
- Every claim must trace back to the input repo.
- The deck is 15 slides, designed for 30 minutes + 15 minutes Q&A.
