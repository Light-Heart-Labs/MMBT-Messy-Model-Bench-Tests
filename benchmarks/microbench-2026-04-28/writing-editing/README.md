# writing editing

> Agent reads a ~1500-word internal outage post-mortem and produces three audience-targeted rewrites: CEO brief (250 words max), customer email (350 words max), legal summary (400 words max). Each has its own must-include and must-not-include lists.
>
> **Pass criteria:** All 3 audience rewrites pass their per-audience required-content / prohibited-content checks; word limits respected.

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 0/3 FAIL | ceo_brief and legal_summary PASS in all 3 runs (5/5 tone fit hand-graded). customer_email FAIL in all 3 — missing required keyword (outage/downtime/incident); agent used softer phrasing ('disruption', 'service issue'). Single-subdimension fail across the entire series. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 2/3 PASS | v1 and v2 all 3 audiences PASS. v3 failed legal_summary (probably included content from the prohibited list). |

## Takeaway

27B's 0/3 isn't a tone-fit failure — it's a single-keyword miss on customer email. Coder-Next ships all three rewrites more reliably.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts live in the source bench repo at `agent-pilot/logs/writing_editing_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
