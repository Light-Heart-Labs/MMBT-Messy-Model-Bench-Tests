# ADR 0001: Risk Scoring Method

## Decision

Score PR risk from 1 to 10 using explicit dimensions: surface area, test coverage, reversibility, blast radius, contributor context, and cross-PR coupling.

## Why

The maintainer needs to clear a backlog, not merely sort by pass/fail. A small docs PR can be risky if it documents insecure behavior, and a large feature can be mergeable if well-contained and proven.

## Consequence

Every `prs/pr-*/verdict.md` includes a numeric score and reasons. The method is documented in `analysis/risk-matrix.md`.
