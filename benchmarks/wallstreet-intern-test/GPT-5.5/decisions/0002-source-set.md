# ADR 0002: Use Company And Regulator Sources As The Evidence Base

Date: 2026-04-27

## Status

Accepted.

## Context

The memo needs every number to be traceable. YETI's SEC filings and company-hosted earnings material cover the core financials, guidance, and management commentary. Market data, consensus, and peer valuation require a third-party market-data source because those figures do not live in SEC filings.

## Alternatives Considered

- SEC filings only: strongest audit trail, but incomplete for current price, market cap, consensus, and peer multiples.
- Company materials plus StockAnalysis: enough to capture filings, releases, transcripts, market data, consensus, and peer metrics with downloadable files and hashes.
- Paid data sources such as Bloomberg or FactSet: better for professional consensus detail, but unavailable in this environment and not reproducible for a stranger cloning the repo.

## Decision

Use SEC/company materials for business and financial evidence. Use StockAnalysis for current market data, consensus, and peer valuation metrics, and record every fetched page in `sources.md` with a SHA-256 hash.

## Consequences

The sell-side comparison is limited to publicly visible consensus fields rather than full analyst models. The upside is that a reviewer can reproduce the evidence from the repo without a paid terminal.
