# ADR 0004: Use A 10.8% WACC And 2.75% Terminal Growth

Date: 2026-04-27

## Status

Accepted.

## Context

YETI is a small/mid-cap discretionary consumer brand with tariff and category-cycle risk, but it also has a net-cash balance sheet on a funded-debt basis and durable free-cash-flow conversion.

## Alternatives Considered

- Use raw five-year beta of 1.798: mechanically higher WACC, but likely overweights recent small-cap volatility.
- Use market beta of 1.0: cleaner for a mature brand, but underweights YETI's discretionary and small-cap risk.
- Blend raw beta and market beta: reduces noise while retaining company-specific cyclicality.
- Terminal growth from 2.0% to 3.0%: range brackets long-run inflation/nominal GDP while leaving room for international growth to fade.

## Decision

Use beta of 1.399, calculated as 50% raw beta and 50% market beta, with a 4.31% 10-year Treasury rate, 5.0% equity-risk premium, 5.5% pre-tax cost of debt, 24% tax rate, and market-cap/debt weights. This produces a WACC of 10.8%. Use 2.75% terminal growth.

## Consequences

The DCF is deliberately not heroic. It credits international runway but still prices the company as a discretionary consumer equity exposed to tariffs and product-cycle risk.
