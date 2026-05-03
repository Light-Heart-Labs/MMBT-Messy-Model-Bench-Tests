# Project management synthesis

> Synthesize 4 weeks of meeting notes into workstream / risk / decision / milestone summary. Programmatic grader: per-element recall.

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 3/3 done | 0.3 min median; $0.0003 — by far the cheapest |
| Qwen3.6-27B-AWQ (thinking) | 3/3 done | 1.3 min median; $0.0017 |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 1.1 min median; $0.0012 |

## Headline

All three ship cleanly. **Both models miss multi-week risks consistently** (workstreams 6/6 every run for both, but only 2-3/6 risks recalled — the multi-week-spanning risks systematically dropped). PASS rate against the per-element rubric needs the grader sweep; this entry reports ship rate only.

## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/project-management/`](../../microbench-2026-04-28/project-management/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/project-management/`](../../microbench-2026-04-28/project-management/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_project_mgmt.md`](../../../tooling/tasks/task_project_mgmt.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
