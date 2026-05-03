# Bug fixing

> Run logalyzer's test suite, find a real bug among the planted issues, ship a fix that makes pytest pass and ruff exit 0. Programmatic grader: `pytest && ruff check && shortcut-signal scan`.

## Results

| Model | Ship rate | Notes |
|---|---|---|
| Qwen3-Coder-Next-AWQ | 2/2 done | 11.5 min median; $0.0148; clean fixes |
| Qwen3.6-27B-AWQ (thinking) | 0/3 done † | 18 min median; the 0/3 baseline is harness-drift sensitive (see Caveats) |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done** | 43 min median; $0.047; clean ships throughout |

## Headline

27B-no-think 10/10 ships at N=10. The 27B-thinking 0/3 from the older harness sha is the headline anomaly; **re-running thinking baselines on the current harness is on the follow-up list**. Per-task quality not deeply graded here; see [`microbench-2026-04-28/bug-fixing/`](../../microbench-2026-04-28/bug-fixing/) for the canonical 2-of-N hand-graded read.

> **† Harness-drift caveat**: 27B-thinking N=3 baselines for this cell used file_sha256 `7698067...` (2026-04-28 batch); the no-think grid used `7ea9592...` (2026-05-02 batch). The 0-1/3 thinking-mode ship rates may include harness-related effects (e.g., the older harness's `model_stopped` floor-failure rate was inflated). The 10/10 no-think result on the current harness is unaffected by this drift. Re-running thinking-mode on the current harness is a recommended follow-up to definitively settle the comparison.


## What's published here

The 12-family no-think drop publishes one representative `done_signal` lean entry per cell (under `Qwen3.6-27B-AWQ-no-think-v1/`) with the standard 5-file metadata. Per-run transcripts and workspace tarballs are in the source bench's `submit/phase-b-overnight-2026-05-02` branch; readers reproducing the bench will produce equivalent artifacts via the [`tooling/`](../../../tooling/) reproduction pack.

Phase B (27B-thinking + Coder-Next) and the original N=3 baselines for this cell are in [`microbench-2026-04-28/bug-fixing/`](../../microbench-2026-04-28/bug-fixing/) where applicable.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model hand-graded quality study (covers `p2_ci`, `p2_extract`, `p2_triage` in depth)
- [`../../microbench-2026-04-28/bug-fixing/`](../../microbench-2026-04-28/bug-fixing/) — the earlier N=3 entry
- [`../../../tooling/tasks/task_code_adoption.md`](../../../tooling/tasks/task_code_adoption.md) — task spec
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
