# DreamServer 75 PR Audit Benchmark

## Prompt

Audit all 75 open pull requests against `Light-Heart-Labs/DreamServer` and
produce a complete triage report with per-PR merge/revise/reject
recommendations, tests/proof notes, cross-PR dependency analysis, maintainer
strategy, and a git repository as the deliverable.

## Why This Is A Messy Benchmark

This task combines:

- live GitHub repository triage,
- large backlog synthesis,
- cross-PR dependency analysis,
- code review,
- test/proof recording,
- repo construction,
- strategic maintainer communication.

The output is not just a final answer. The model has to build a durable,
navigable audit repository with traceability for every verdict.

## Model Entries

| Model | Entry | Final Tally |
|---|---|---|
| GPT-5.5 | `GPT-5.5/` | 34 Merge / 40 Revise / 1 Reject |
| Claude Opus 4.7 (1M context) | `Opus-4.7/` | 53 Merge / 6 Revise-small / 1 Revise-arch / 1 Reject / 14 Hold |

The two entries use different verdict frameworks. GPT-5.5 uses a 3-bucket
Merge/Revise/Reject taxonomy. Opus-4.7 introduces a Hold category for
"needs maintainer judgment" decisions, splits Revise into small /
missing-tests / architectural, and uses an explicit 5-axis 0-20 risk score
documented as an ADR (`Opus-4.7/decisions/0001-risk-scoring-methodology.md`).
Both methodologies are reasonable; the ADR is what makes the Opus-4.7
verdicts comparable on their own terms.

## Expected Entry Shape

Each model entry should preserve its own artifact structure. The shared
shape is:

- `report/`
- `prs/pr-{number}/`
- `testing/`
- `analysis/`
- `research/`
- `decisions/`
- `sources.md`
- `tool-log.md`

Both current entries follow this shape. The Opus-4.7 entry adds an
`ACTIONABLE_FINDINGS_INDEX.md` at its root for fast scan of line-level
issues, mirroring GPT-5.5's similar index file.
