# Test writing

> Add tests to logalyzer with a coverage-delta requirement and a production-code-unchanged check. **Same task-design issue as refactoring**: the starter has a broken import that requires touching production code to fix.

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 2/3 done | 14 min median; $0.0182; ships but PASS rate gated by task-design issue |
| Qwen3.6-27B-AWQ (thinking) | 0/3 done † | 9.6 min median; ship rate harness-drift sensitive |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 20 min median; $0.0214 |

## Headline

27B-no-think 10/10 ships at N=10. Same task-design caveat as refactoring — PASS rate against the rubric isn't decoupled from the broken-starter issue.

> **† Harness-drift caveat**: 27B-thinking N=3 baselines for this cell used file_sha256 `7698067...` (2026-04-28 batch); the no-think grid used `7ea9592...` (2026-05-02 batch). The 0-1/3 thinking-mode ship rates may include harness-related effects (e.g., the older harness's `model_stopped` floor-failure rate was inflated). The 10/10 no-think result on the current harness is unaffected by this drift. Re-running thinking-mode on the current harness is a recommended follow-up to definitively settle the comparison.


## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/test-writing/`](../../microbench-2026-04-28/test-writing/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/test-writing/`](../../microbench-2026-04-28/test-writing/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_test_writing.md`](../../../tooling/tasks/task_test_writing.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
