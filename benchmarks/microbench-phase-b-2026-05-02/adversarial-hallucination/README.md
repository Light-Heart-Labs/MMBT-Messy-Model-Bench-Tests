# Adversarial hallucination

> Classify 15 issues (6 real / 9 fabricated) — resistance to confident-but-wrong claims.

## Results — N=10 across all three model arms

| Model | Ship rate | Pathology profile | Lean entry |
|---|---|---|---|
| Qwen3-Coder-Next-AWQ | 5/10 done_signal | 5/10 stuck_no_workspace_change | [v1-stuck/](Qwen3-Coder-Next-AWQ-v1-stuck/) |
| Qwen3.6-27B-AWQ (thinking) | 7/10 done_signal | 3/10 model_stopped (older harness) | [v1/](Qwen3.6-27B-AWQ-v1/) |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10 done_signal** | 0 pathology | [v1/](Qwen3.6-27B-AWQ-no-think-v1/) |

## Headline

27B-no-think is the cleanest of the three on this cell (10/10), with 27B-thinking second (7/10) and Coder-Next showing the documented hallucination-resistance gap (5/10 stuck). The Coder-Next stuck rate at N=10 is bounded by Wilson 95% [23.7%, 76.3%] — confirmed reproducible failure shape, not a 1-of-N flake.

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model quality study with hand-graded axes (only `p2_ci`, `p2_extract`, `p2_triage` graded so far; this cell deferred to follow-up)
- [`../../microbench-2026-04-28/adversarial-hallucination/`](../../microbench-2026-04-28/adversarial-hallucination/) — earlier N=3 entry with full per-model READMEs at the smaller sample size
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
