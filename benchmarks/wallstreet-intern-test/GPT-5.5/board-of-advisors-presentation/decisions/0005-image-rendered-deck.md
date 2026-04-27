# ADR 0005: Build The Deck From Deterministic Slide Renders

Date: 2026-04-27

## Status

Accepted.

## Context

The board deck must ship as PPTX and PDF, and the visual evidence needs to be reproducible on a fresh Linux VM. This environment has `python-pptx` and Pillow, but no PowerPoint or LibreOffice renderer for checking native PPTX layout fidelity.

## Alternatives Considered

- Native editable PPTX shapes only: more editable, but hard to render and verify without an installed presentation renderer.
- PDF-only deck: visually deterministic, but fails the requested PPTX deliverable.
- Image-rendered slides inserted into PPTX: less editable, but the deck, PDF, and PNG previews are produced from the same source and can be visually checked deterministically.

## Decision

Generate each slide as a 1600 x 900 PNG from `deck/source/build_deck.py`, assemble those images into the PPTX, and export the same PNG set into a PDF. Keep every chart separately reproducible from `assets/charts/build_charts.py` and every diagram separately reproducible from `assets/diagrams/build_diagrams.py`.

## Consequences

The delivered PPTX is optimized for auditability and deterministic reproduction rather than native slide editing. This is acceptable for the board-readout use case because the repo, not only the deck binary, is the deliverable.
