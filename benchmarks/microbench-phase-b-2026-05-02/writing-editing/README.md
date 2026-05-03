# Writing/editing

> Audience-tailored rewrite (CEO brief / customer email / legal summary) of a single source doc with per-audience must-include / must-not-include rules. Programmatic grader: per-audience subdimension PASS.

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 3/3 done | 0.4 min median; $0.0005 |
| Qwen3.6-27B-AWQ (thinking) | 3/3 done | 2.8 min median; $0.0036 |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 2.1 min median; $0.0023 |

## Headline

All three ship reliably. PASS rate at N=3 was uneven on the original microbench (27B 0/3 due to single-subdimension fails on customer_email; Coder 2/3); re-grading at N=10 with the no-think arm needs the grader sweep.

## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/writing-editing/`](../../microbench-2026-04-28/writing-editing/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/writing-editing/`](../../microbench-2026-04-28/writing-editing/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_writing_editing.md`](../../../tooling/tasks/task_writing_editing.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
