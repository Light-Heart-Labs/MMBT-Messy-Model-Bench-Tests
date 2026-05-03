# Findings index

Cross-cutting analyses that synthesize across multiple model entries or benchmark runs. Listed newest-first.

| Doc | Date | One-line summary |
|---|---|---|
| [`microbench-phase-b-2026-05-02/findings.md`](microbench-phase-b-2026-05-02/findings.md) | 2026-05-02 | N=10 expansion + 27B-no-think third arm. Three identical-call-loop subclasses (`scroll-loop`, `word-trim-loop`, `rewrite-loop`). Per-cell ship rates with Wilson CIs, cost-per-shipped-run, "when to use which" updates. |
| [`microbench-phase-b-2026-05-02/findings-pairwise-quality-three-model.md`](microbench-phase-b-2026-05-02/findings-pairwise-quality-three-model.md) | 2026-05-03 | Hand-graded deliverable quality study on the both-ship cells (p2_ci, p2_extract, p2_triage). Headline: 27B-thinking and 27B-no-think substantively equivalent on output decisions; Coder-Next has a distinct reasoning style. **Includes a load-bearing correction to the 2026-04-28 study's `p2_ci` regression attribution.** |
| [`microbench-2026-04-28/findings.md`](microbench-2026-04-28/findings.md) | 2026-04-28 | Original 12-task-family × 2-model × N=3 microbench writeup. Daily-driver guide framework, 27B word-limit-trim failure mode, market-research inversion (27B drives internet research that Coder-Next doesn't). Still load-bearing for the 8 cells phase-b didn't expand. |
| [`dreamserver-75-pr-audit/findings-2026-04-27-local-models.md`](dreamserver-75-pr-audit/findings-2026-04-27-local-models.md) | 2026-04-27 | Cross-cutting comparison of the local-model entries against the cloud entries on the 75-PR audit. Documents the categorical cloud-vs-local gap and the per-local-model failure shapes. |
| [`dreamserver-1-pr-audit/findings-2026-04-27-strict-done-ablation.md`](dreamserver-1-pr-audit/findings-2026-04-27-strict-done-ablation.md) | 2026-04-27 | Ablation: does enforcing a strict `done()` requirement change the verdict-accuracy picture on the 1-PR audit? |

## Reading order recommendations

**For the 5-minute model-selection question**: Start with [`../COMPARISON.md`](../COMPARISON.md), not the findings docs. The findings docs are the evidence base; COMPARISON is the synthesis.

**For the most current N=10 picture**: `microbench-phase-b-2026-05-02/findings.md`.

**For deliverable-quality differences when models all ship**: `findings-pairwise-quality-three-model.md`.

**For long-horizon agentic failure modes**: `dreamserver-75-pr-audit/findings-2026-04-27-local-models.md`.

**For the original 12-cell N=3 baseline (still current for the 8 non-Phase-B cells)**: `microbench-2026-04-28/findings.md`.
