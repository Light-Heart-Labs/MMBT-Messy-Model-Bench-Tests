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

| Model | Entry |
|---|---|
| GPT-5.5 | `GPT-5.5/` |

## Expected Entry Shape

Each model entry should preserve its own artifact structure. For the GPT-5.5
entry, that includes:

- `report/`
- `prs/pr-{number}/`
- `testing/`
- `analysis/`
- `research/`
- `decisions/`
- `sources.md`
- `tool-log.md`
