# Document synthesis

> Distill 12 PRs into a brief.md ≤700 words capturing 8 planted facts.

## Results — N=10 across all three model arms

| Model | Ship rate | Pathology profile | Lean entry |
|---|---|---|---|
| Qwen3-Coder-Next-AWQ | 10/10 done_signal | 0 pathology | [v1/](Qwen3-Coder-Next-AWQ-v1/) |
| Qwen3.6-27B-AWQ (thinking) | 6/10 done_signal | **4/10 wall_killed_identical_call_loop** (the documented word-trim loop) | [v2-wall-killed/](Qwen3.6-27B-AWQ-v2-wall-killed/) |
| **Qwen3.6-27B-AWQ (no-think)** | **8/10 done_signal** | 2/10 wall_killed_identical_call_loop | [v1/](Qwen3.6-27B-AWQ-no-think-v1/) |

## Headline

**This is the cell where disabling thinking measurably helps.** 27B-thinking hits a stable ~40% rate of wall_killed_identical_call_loop (4/10 at N=10, Wilson 95% [16.8%, 68.7%]) — the documented word-limit-trim loop. **27B-no-think drops the loop rate to 2/10**, taking ship rate from 6/10 → 8/10. Coder-Next remains the operational pick at 10/10, but if you need the 27B reasoning style for this task, **use no-think**.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model quality study with hand-graded axes (only `p2_ci`, `p2_extract`, `p2_triage` graded so far; this cell deferred to follow-up)
- [`../../microbench-2026-04-28/doc-synthesis/`](../../microbench-2026-04-28/doc-synthesis/) — earlier N=3 entry with full per-model READMEs at the smaller sample size
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
