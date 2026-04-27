# ADR 0005: Blend DCF, EV/EBITDA, And P/E For The 12-Month Target

Date: 2026-04-27

## Status

Accepted.

## Context

The PM-facing recommendation needs a 12-month price target. A pure DCF captures long-run cash generation, while trading multiples capture where branded consumer-products equities are being valued today.

## Alternatives Considered

- Pure DCF: cleanest theory, but too sensitive to WACC and terminal assumptions.
- Pure multiple: market-aware, but can overfit current sentiment and ignore cash generation.
- Consensus target: useful reference, but not an independent recommendation.

## Decision

Use a blended target: 50% DCF, 25% FY2026 EV/EBITDA, and 25% FY2026 P/E. Use an 11.5x EBITDA exit multiple and 16.0x P/E as a YETI-specific cross-check near current trading context but below the strongest premium peer. Recommend `HOLD` unless risk-adjusted upside exceeds 20% or downside exceeds 15%.

## Consequences

The target is $41 per share, only 3.5% above the fetched $39.62 share price, which points to `HOLD` rather than a directional call.
