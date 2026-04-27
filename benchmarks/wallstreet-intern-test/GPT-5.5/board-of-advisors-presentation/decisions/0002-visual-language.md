# ADR 0002: Use A Distinct Audit-Led Palette And Chart Convention

Date: 2026-04-27

## Status

Accepted.

## Context

The deck needs to be colorful and distinctive without looking like decorative finance theater. Color should encode meaning consistently across slides.

## Alternatives Considered

- YETI-like neutral outdoor palette: on-brand, but risks becoming beige/green and less useful for scenario semantics.
- Standard finance blue/gray palette: legible, but generic and weak for a capability demonstration.
- Audit-led dark ink with high-contrast scenario colors: distinctive, readable, and semantically useful.

## Decision

Use deep ink as the base, off-white slide fields, and four semantic accent colors:

- Base case / current call: blue.
- Bear / downside: red.
- Bull / upside: green.
- Audit / traceability: amber.

Charts use the same scenario colors throughout. Trace IDs use amber so the audit mechanism is visible but not louder than the data.

## Consequences

The visual system reinforces the difference between recommendation, uncertainty, and audit trail. Decorative color is minimized; data color is consistent.
