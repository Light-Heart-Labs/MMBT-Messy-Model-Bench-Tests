# MMBT - Messy Model Bench Tests

This repository stores messy, real-world benchmark outputs from different
models. Each benchmark is a task that looks like actual project work rather
than a tidy synthetic eval.

## Layout

```text
benchmarks/
  dreamserver-75-pr-audit/
    GPT-5.5/
      report/
      prs/
      analysis/
      testing/
      research/
      decisions/
    Opus-4.7/
      report/
      prs/
      analysis/
      testing/
      research/
      decisions/
  wallstreet-intern-test/
    GPT-5.5/
      memo/
      model/
      raw/
      extracted/
      analysis/
      research/
      decisions/
```

## Benchmarks

| Benchmark | Prompt Shape | Model Entries |
|---|---|---|
| `dreamserver-75-pr-audit` | Audit 75 open PRs in a live repository and produce a traceable maintainer triage repo. | `GPT-5.5`, `Opus-4.7` |
| `wallstreet-intern-test` | Build a traceable investment memo repo with raw sources, extracted data, a three-statement model, valuation, and recommendation. | `GPT-5.5` |

## How To Read A Model Entry

Start with the benchmark folder README, then open the model folder:

1. `benchmarks/<benchmark>/README.md`
2. `benchmarks/<benchmark>/<model>/README.md`
3. The model entry's README for its artifact-specific read order, then the main deliverables such as `report/` / `prs/` or `memo/` / `model/`.

## Current Entries

- DreamServer 75 PR Audit / GPT-5.5: `benchmarks/dreamserver-75-pr-audit/GPT-5.5/`
- DreamServer 75 PR Audit / Claude Opus 4.7 (1M context): `benchmarks/dreamserver-75-pr-audit/Opus-4.7/`
- Wallstreet Intern Test / GPT-5.5: `benchmarks/wallstreet-intern-test/GPT-5.5/`
