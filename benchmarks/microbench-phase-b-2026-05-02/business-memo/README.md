# Business memo

> Read an acquisition deal pack on Borealis Analytics with 8 planted bias signals; write an investment memo for the buy-side committee within 700 words.

## Results — N=10 across all three model arms

| Model | Ship rate | Pathology profile | Lean entry |
|---|---|---|---|
| Qwen3-Coder-Next-AWQ | 10/10 done_signal | 0 pathology — fastest at $0.0006/ship | [v1/](Qwen3-Coder-Next-AWQ-v1/) |
| Qwen3.6-27B-AWQ (thinking) | 9/10 done_signal | 1 wall_killed_identical_call_loop | [v1/](Qwen3.6-27B-AWQ-v1/) |
| Qwen3.6-27B-AWQ (no-think) | 8/10 done_signal | 2 wall_killed_identical_call_loop | [v1/](Qwen3.6-27B-AWQ-no-think-v1/) |

## Headline

Coder-Next wins this cell — 10/10 ship at ~$0.0006/ship (60-100× cheaper than either 27B variant). Both 27B variants hit a small wall_killed_identical_call_loop rate (10-20%), making them less reliable on this task class even when they ship cleanly. **For business-memo workloads where ship rate matters more than reasoning depth, Coder-Next is the clear pick.**

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model quality study with hand-graded axes (only `p2_ci`, `p2_extract`, `p2_triage` graded so far; this cell deferred to follow-up)
- [`../../microbench-2026-04-28/business-memo/`](../../microbench-2026-04-28/business-memo/) — earlier N=3 entry with full per-model READMEs at the smaller sample size
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
