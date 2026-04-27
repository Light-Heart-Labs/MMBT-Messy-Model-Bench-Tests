# ADR 0003: Use GOLF, MAT, And NWL As The Core Public Peer Set

Date: 2026-04-27

## Status

Accepted.

## Context

YETI is a branded consumer-products company with outdoor, recreation, drinkware, and wholesale/DTC exposure. No public peer is perfect: premium drinkware brands are often private or embedded inside larger companies.

## Alternatives Considered

- Acushnet (`GOLF`): premium recreation equipment, stronger brand/enthusiast angle, higher multiple.
- Mattel (`MAT`): branded consumer-products portfolio, global distribution, lower growth/multiple profile.
- Newell Brands (`NWL`): consumer household portfolio with large drinkware/container exposure, but weaker growth and higher leverage.
- Solo Brands (`DTC`): closer DTC/outdoor adjacency, but market cap and profitability profile are distressed and no longer useful for a core valuation median.

## Decision

Use `GOLF`, `MAT`, and `NWL` as the core peer context. Keep `DTC` in the raw peer file as a checked data point, but exclude it from the core triangulation because its market cap and negative operating margin would distort the comparison.

## Consequences

The valuation memo treats peer multiples as context rather than a mechanical comp set. The final target uses YETI's own DCF as the anchor and multiples as a cross-check.
