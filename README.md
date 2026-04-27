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
```

## Benchmarks

| Benchmark | Prompt Shape | Model Entries |
|---|---|---|
| `dreamserver-75-pr-audit` | Audit 75 open PRs in a live repository and produce a traceable maintainer triage repo. | `GPT-5.5`, `Opus-4.7` |

## How To Read A Model Entry

Start with the benchmark folder README, then open the model folder:

1. `benchmarks/<benchmark>/README.md`
2. `benchmarks/<benchmark>/<model>/README.md`
3. The model's `report/`, `analysis/`, and `prs/` artifacts

## Current Entries

- GPT-5.5: `benchmarks/dreamserver-75-pr-audit/GPT-5.5/`
- Claude Opus 4.7 (1M context): `benchmarks/dreamserver-75-pr-audit/Opus-4.7/`
