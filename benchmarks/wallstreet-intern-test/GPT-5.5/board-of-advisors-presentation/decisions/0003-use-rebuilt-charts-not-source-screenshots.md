# ADR 0003: Rebuild Evidence As Charts And Diagrams Instead Of Screenshots

Date: 2026-04-27

## Status

Accepted.

## Context

The input repo contains PDFs, HTML filings, transcript text, extracted CSVs, and model output. A board deck could show screenshots of those artifacts, but screenshots are hard to read and weakly editable.

## Alternatives Considered

- Use source-document screenshots: faithful, but visually noisy and not presentation-native.
- Use only open text: clean, but underuses the rich model and trace data.
- Rebuild charts/diagrams from extracted data: readable and reproducible.

## Decision

Use generated charts, tables, and diagrams built from input-repo data. Keep screenshots out of the deck except if needed as an audit artifact, which is not currently planned.

## Consequences

Every chart must have a script and source CSV in `/assets/charts/` and `/assets/tables/`. This adds work, but directly supports the prompt's reproducibility requirement.
