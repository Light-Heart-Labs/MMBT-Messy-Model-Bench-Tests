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
```

## Benchmarks

| Benchmark | Prompt Shape | Model Entries |
|---|---|---|
| `dreamserver-75-pr-audit` | Audit 75 open PRs in a live repository and produce a traceable maintainer triage repo. | `GPT-5.5` |

## How To Read A Model Entry

Start with the benchmark folder README, then open the model folder:

1. `benchmarks/<benchmark>/README.md`
2. `benchmarks/<benchmark>/<model>/README.md`
3. The model's `report/`, `analysis/`, and `prs/` artifacts

## Current Entry

GPT-5.5's DreamServer 75-PR audit is here:

`benchmarks/dreamserver-75-pr-audit/GPT-5.5/`
