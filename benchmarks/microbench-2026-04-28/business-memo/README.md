# business memo

> Agent reads an acquisition deal pack on Borealis Analytics with 8 planted bias signals (cherry-picked metrics, reframed losses, omitted competition, etc.) and writes an investment memo for the buy-side committee. Memo must catch the bias signals and push back.
>
> **Pass criteria:** ≥6 of 8 planted bias signals captured and pushed back against; memo within 700-word limit; explicit stance.

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 2/3 PASS | 8/8 bias signals captured every run. v3 hit 708 words (1 over limit). 2.8 min median wall. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 3/3 PASS | 6-8/8 bias signals captured every run. All 3 runs within word limit. 0.5 min median wall — 5× faster than 27B and 5× cheaper. |

## Takeaway

Both reliable on bias-detection. Coder-Next ships within the word limit consistently; 27B occasionally hits the trim issue (1 word over on v3). For this task class, Coder-Next is the operational pick.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts are not mirrored in MMBT for the lean entries (saves repo space). With the task prompt, input starter, and grader script in [`../../../tooling/`](../../../tooling/), readers can rerun the task family themselves to produce equivalent artifacts. Bench-side log dir naming was `agent-pilot/logs/p3_business_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
