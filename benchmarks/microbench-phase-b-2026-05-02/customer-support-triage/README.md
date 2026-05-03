# Customer support triage

> Closed-vocabulary classification of 30 support tickets across categories + duplicate-cluster recall. Programmatic grader: category accuracy + dup-cluster recall thresholds.

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 3/3 done | 1.0 min median; 96.7% category accuracy, 100% dup-cluster recall — best on category accuracy |
| Qwen3.6-27B-AWQ (thinking) | 3/3 done | 3.3 min median; 86.7% accuracy, 100% dup-cluster recall |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 2.6 min median; same category accuracy as thinking-mode (86.7%), 100% dup-cluster recall |

## Headline

All three ship reliably. Coder-Next leads on category accuracy (96.7% vs 86.7% for both 27B variants) and is 3× faster. The original 2026-04-28 study identified an 'urgency-calibration gap' between 27B-family and Coder-Next; the gap persists at N=10 with 27B-no-think aligning with thinking-mode, not with Coder-Next.

## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/customer-support-triage/`](../../microbench-2026-04-28/customer-support-triage/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/customer-support-triage/`](../../microbench-2026-04-28/customer-support-triage/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_triage.md`](../../../tooling/tasks/task_triage.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
