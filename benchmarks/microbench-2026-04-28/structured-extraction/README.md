# structured extraction

> Agent reads a fictional press release (Veridyne Networks, ~1500 words) and produces JSON matching a 20-field schema. Fields include company name, products, pricing, executives, dates, locations, etc.
>
> **Pass criteria:** ≥80% of 20 fields exactly match ground truth (with type-aware tolerance for numbers and dates).

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 3/3 PASS | **100% accuracy across all 20 fields, all 3 runs.** This is the kind of result you'd build a pipeline on. 1.2 min median wall, $0.0015 cost. The single sharpest accuracy demonstration in the entire microbench. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 3/3 PASS | ~92% median accuracy (well above 80% threshold). Faster (~0.3 min) and 4× cheaper than 27B. |

## Takeaway

Both models PASS reliably; 27B is more accurate; Coder-Next is faster and cheaper. Pick by cost-vs-accuracy preference.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts are not mirrored in MMBT for the lean entries (saves repo space). With the task prompt, input starter, and grader script in [`../../../tooling/`](../../../tooling/), readers can rerun the task family themselves to produce equivalent artifacts. Bench-side log dir naming was `agent-pilot/logs/p2_extract_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
