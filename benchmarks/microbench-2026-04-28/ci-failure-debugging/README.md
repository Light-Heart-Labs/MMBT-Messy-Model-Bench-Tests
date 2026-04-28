# ci failure debugging

> Agent receives a Python project (discountkit) with 3 planted bugs that cause `ruff` and `pytest` to fail in CI. Must read the CI failure log, find the bugs, fix them, and produce a clean repo.
>
> **Pass criteria:** ruff exits 0; pytest exits 0; no test-disabling or `# noqa` shortcuts; suspicious pyproject.toml changes flagged.

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 3/3 PASS | Clean — ruff green, pytest green, no shortcuts. 2.1 min median wall. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 3/3 PASS | Clean — same. 1.2 min median wall (faster), 2× cheaper than 27B. |

## Takeaway

Both models 3/3 PASS. CI-failure-debugging is a tight, well-defined task class; pick the cheaper model.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts are not mirrored in MMBT for the lean entries (saves repo space). With the task prompt, input starter, and grader script in [`../../../tooling/`](../../../tooling/), readers can rerun the task family themselves to produce equivalent artifacts. Bench-side log dir naming was `agent-pilot/logs/p2_ci_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
