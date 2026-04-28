# test writing

> Agent receives the `logalyzer/` package with low test coverage and is asked to write additional tests targeting specific uncovered branches. Production code must remain unchanged.
>
> **Pass criteria:** Coverage delta ≥10% over baseline; production code unchanged (`git diff src/` is empty); new tests actually exercise new branches.

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 0/3 FAIL | Task-design issue: starter has a known broken import (`from collections import Iterable`, removed in Python 3.10+). Pytest can't collect tests. Agent has to either fix the production import (violating the unchanged-production rule) or work around it. 0/3 PASS reflects the design conflict, not pure model failure. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 0/3 FAIL | Same task-design issue affects Coder-Next identically. |

## Takeaway

Failure here is a starter-codebase issue (broken import requires production-code fix to satisfy 'tests must collect'), not a model-quality signal. See findings.md § 'Test-writing and refactoring task-design issue' before drawing conclusions from this row.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts are not mirrored in MMBT for the lean entries (saves repo space). With the task prompt, input starter, and grader script in [`../../../tooling/`](../../../tooling/), readers can rerun the task family themselves to produce equivalent artifacts. Bench-side log dir naming was `agent-pilot/logs/p1_testwrite_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
