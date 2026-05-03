# Refactoring

> Localized refactor of logalyzer with strict no-bleed; add an `output/` subpackage; tests still pass. Programmatic grader: structural check + tests-still-pass + bleed-detector. **Known task-design issue**: the starter has a broken `from collections import Iterable` (Python 3.10+ removed this) — both Coder-Next and 27B-thinking 0/3 PASS on the original microbench, but the failure is starter-vs-task-scope tension, not pure model behavior.

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 3/3 done (ship) | 5.4 min median; $0.0070; ships but PASS rate gated by task-design issue |
| Qwen3.6-27B-AWQ (thinking) | 1/3 done † | 5.4 min median; ship rate harness-drift sensitive |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 9.4 min median; $0.0101 |

## Headline

27B-no-think 10/10 ships at N=10. PASS rate (does the refactor hit the structural rubric?) is task-design-issue-dominated and not re-graded here. See [`microbench-2026-04-28/findings.md`](../../microbench-2026-04-28/findings.md) § 'Test-writing and refactoring task-design issue' for the underlying issue with the starter.

> **† Harness-drift caveat**: 27B-thinking N=3 baselines for this cell used file_sha256 `7698067...` (2026-04-28 batch); the no-think grid used `7ea9592...` (2026-05-02 batch). The 0-1/3 thinking-mode ship rates may include harness-related effects (e.g., the older harness's `model_stopped` floor-failure rate was inflated). The 10/10 no-think result on the current harness is unaffected by this drift. Re-running thinking-mode on the current harness is a recommended follow-up to definitively settle the comparison.


## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/refactoring/`](../../microbench-2026-04-28/refactoring/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/refactoring/`](../../microbench-2026-04-28/refactoring/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_refactoring.md`](../../../tooling/tasks/task_refactoring.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
