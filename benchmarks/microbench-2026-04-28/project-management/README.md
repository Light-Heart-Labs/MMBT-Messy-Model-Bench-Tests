# project management

> Agent reads 6 weeks of Project Aurora meeting notes (recurring weekly status meetings, ~3000 words total) and produces a structured roadmap: 6 workstreams, 4 decisions made, 6 open risks (some of which span multiple weeks), 5 milestones.
>
> **Pass criteria:** Workstream recall ≥5/6; risk recall ≥3/6; decision recall ≥3/4; milestone recall ≥4/5.

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 0/3 FAIL | Workstreams 6/6 every run, decisions 3-4/4, milestones 5/5. **Risks 2/6 across all runs** — multi-week-spanning risks systematically dropped. FAIL on risk threshold. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 1/3 PASS | Workstreams 6/6 every run, decisions 3-4/4, milestones 4-5/5. Risks 2-3/6 — same multi-week-risk-miss pattern. v2 squeaked over the 3/6 risk threshold. |

## Takeaway

Both models are excellent at workstream/decision/milestone recall and bad at multi-week-spanning risks. The risk-recall gap is task-shape (model can identify risks mentioned in one week, struggles to track risks raised in week 2 and resurfaced in week 5), not model-specific.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts live in the source bench repo at `agent-pilot/logs/project_management_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
