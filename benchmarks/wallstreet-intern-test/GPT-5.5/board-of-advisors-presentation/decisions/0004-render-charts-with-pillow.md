# ADR 0004: Render Reproducible Charts With Pillow

Date: 2026-04-27

## Status

Accepted.

## Context

The available system Python has `python-pptx` and Pillow, but not `matplotlib` or Plotly. The bundled runtime has ReportLab but not `python-pptx`.

## Alternatives Considered

- Install new plotting dependencies: possible with internet, but adds dependency churn and weakens the reproducibility story.
- Use screenshots from spreadsheets or PDFs: fast, but violates the rebuilt-chart intent and is less legible.
- Use Pillow to draw deterministic chart PNGs from CSV tables: lightweight, reproducible, and enough for this deck's visual needs.

## Decision

Generate all chart PNGs with `assets/charts/build_charts.py` and all process diagrams with `assets/diagrams/build_diagrams.py`, using CSVs produced from the input repo.

## Consequences

The charts are image assets rather than native PowerPoint charts. The tradeoff is acceptable here because every chart has a script and source table, and the deck is an audit demonstration rather than an editable model workbook.
