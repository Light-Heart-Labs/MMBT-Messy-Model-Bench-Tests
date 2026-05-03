# CI failure debugging

> Read failing CI log for `discountkit`, target-fix three planted bugs (unused import, missing `/100` in `discount_amount`, stale `line_count` test against the v0.3.0 API change), re-run CI checks. Both 27B variants and Coder-Next pass the binary grader at N=3-10. **The hand-graded quality study** ([`findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md)) found the load-bearing finding: Coder-Next regresses the `line_count` API by trusting the test name over the CHANGELOG; both 27B variants correctly trust the docs.

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 3/3 done (binary PASS) | 1.2 min median; $0.0015 — but **regresses the v0.3.0 API in v1** |
| Qwen3.6-27B-AWQ (thinking) | 3/3 done | 2.1 min median; $0.0027 — preserves v0.3.0 |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 1.8 min median; $0.0020 — preserves v0.3.0 (consistent with thinking-mode) |

## Headline

All three models pass the binary grader, but per-fix quality differs. **For tasks where there's a CHANGELOG / API contract / external-spec resolution, prefer 27B (either mode); Coder-Next trusts test names over docs and regresses on this kind of conflict.** See the pairwise quality study for the full analysis.

## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/ci-failure-debugging/`](../../microbench-2026-04-28/ci-failure-debugging/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/ci-failure-debugging/`](../../microbench-2026-04-28/ci-failure-debugging/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_ci_failure.md`](../../../tooling/tasks/task_ci_failure.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
