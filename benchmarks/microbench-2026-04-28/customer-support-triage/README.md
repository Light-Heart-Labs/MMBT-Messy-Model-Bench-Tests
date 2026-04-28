# customer support triage

> Agent receives 30 hand-written customer support tickets and must (1) classify each into one of 8 categories and (2) cluster duplicates (some tickets are paraphrases of the same underlying issue).
>
> **Pass criteria:** Category accuracy ≥70%; duplicate-cluster recall ≥80%.

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 3/3 PASS | 86.7% category accuracy, 100% duplicate-cluster recall every run. 3.3 min median wall. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 3/3 PASS | **96.7% category accuracy** (better than 27B), 100% duplicate-cluster recall every run. 1.0 min median wall, ~3× cheaper than 27B. |

## Takeaway

Both PASS. Coder-Next is slightly more accurate AND faster AND cheaper here — clear win for Coder-Next on this task class.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts are not mirrored in MMBT for the lean entries (saves repo space). With the task prompt, input starter, and grader script in [`../../../tooling/`](../../../tooling/), readers can rerun the task family themselves to produce equivalent artifacts. Bench-side log dir naming was `agent-pilot/logs/p2_triage_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
