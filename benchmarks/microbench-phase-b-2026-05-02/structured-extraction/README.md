# Structured extraction

> Read a Veridyne Networks Q3 FY2026 press release; produce JSON matching a 20-field schema with hedging-language disambiguation per field-specific rules. Programmatic grader: per-field exact-match (with tolerance).

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 3/3 done | 0.3 min median; $0.0004 — fastest; ~92% accuracy on 20 fields |
| Qwen3.6-27B-AWQ (thinking) | 3/3 done | 1.2 min median; $0.0015 — 100% accuracy; dense inline reasoning |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 0.8 min median; $0.0009 — 100% accuracy; sparse reasoning prose |

## Headline

All three ship reliably. **27B has a higher accuracy ceiling (100% vs ~92% for Coder-Next)** but Coder-Next is 4× faster and cheaper. No-think preserves 27B's accuracy advantage with leaner output. For downstream JSON consumers, choose by speed/cost; for human readers tracing per-field reasoning, prefer 27B-thinking.

## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/structured-extraction/`](../../microbench-2026-04-28/structured-extraction/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/structured-extraction/`](../../microbench-2026-04-28/structured-extraction/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_extraction.md`](../../../tooling/tasks/task_extraction.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
