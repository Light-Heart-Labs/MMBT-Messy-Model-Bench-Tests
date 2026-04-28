# refactoring

> Agent must extract the output-formatting logic from the monolithic `parser.py` into a new `output/` subpackage. Tests must still pass after the refactor; no behavioral change.
>
> **Pass criteria:** `output/` subpackage created; existing tests pass; no behavioral drift in `parser.py`'s public API.

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 0/3 FAIL | Same broken-import task-design issue as test-writing. Agent DID create the `output/` subpackage in 3/3 runs but couldn't make tests pass. 5.4 min median wall. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 0/3 FAIL | Same — created `output/` subpackage in 3/3 but tests don't collect. |

## Takeaway

Same task-design issue as test-writing. Both models attempted the refactor structurally; the broken import blocks the test-passes-after-refactor pass criterion.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts are not mirrored in MMBT for the lean entries (saves repo space). With the task prompt, input starter, and grader script in [`../../../tooling/`](../../../tooling/), readers can rerun the task family themselves to produce equivalent artifacts. Bench-side log dir naming was `agent-pilot/logs/p1_refactor_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
