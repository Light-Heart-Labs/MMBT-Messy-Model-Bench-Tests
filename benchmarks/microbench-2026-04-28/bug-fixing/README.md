# bug fixing

> Agent receives the `logalyzer/` Python package with 8 deliberately-planted bugs (off-by-one, wrong return type, missing edge case, etc.) and a failing pytest suite. Must fix the bugs so pytest passes.
>
> **Pass criteria:** pytest passes (originally failing tests now green); production code modified appropriately; no test-disabling shortcuts (`@pytest.mark.skip`, `xfail`).

## Results — N=3 per model

| Model | Verdict | Notes |
|---|---|---|
| **[Qwen3.6-27B-AWQ](./Qwen3.6-27B-AWQ/)** | 3/3 PASS | All 3 runs pytest 0→17, 0→63, 0→55 passing tests. Runs took 18 min median ($0.023). Reliable bug-fixing across N=3. |
| **[Qwen3-Coder-Next-AWQ](./Qwen3-Coder-Next-AWQ/)** | 2/3 PASS | v1 and v2 PASS; v3 was killed at iter 540 / 110 min after post-completion drift (model started running `rm -rf repo` operations destroying its own work after tagging v0.3.0). 12 min median ($0.015) for the shipping runs. |

## Takeaway

Both models can fix planted bugs. 27B is more reliable across N=3; Coder-Next is faster and cheaper per attempt but the v3 post-completion drift is a documented failure mode.

## What's published

This is a **lean entry** — only `cost.json`, `grade.json`, `label.json`, `summary.json`, and `receipt.json` are mirrored from the source bench repo for one representative run per model (the v1 run; full N=3 results live in `findings.md` / `SCORECARD.md`). Transcripts and deliverable artifacts live in the source bench repo at `agent-pilot/logs/bug_fixing_*` for those who want to drill in. See [`microbench-2026-04-28/README.md`](../README.md) § "What's published here" for the rationale.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../../../SCORECARD.md`](../../../SCORECARD.md) § microbench-2026-04-28 — single-table summary including this task family
