# Market research

> Evaluate 5 password-manager products (1Password, Bitwarden, LastPass, Dashlane, Keeper) with live-network research and citations; produce a recommendation memo within 700 words.

## Results — N=10 across all three model arms

| Model | Ship rate | Pathology profile | Lean entry |
|---|---|---|---|
| Qwen3-Coder-Next-AWQ | **0/10 done_signal** | 5 stuck + 4 api_error: HTTP 400 + 1 wall_killed | [v1-stuck/](Qwen3-Coder-Next-AWQ-v1-stuck/), [v3-api-error/](Qwen3-Coder-Next-AWQ-v3-api-error/) |
| **Qwen3.6-27B-AWQ (thinking)** | **8/10 done_signal** | 2 api_error retried (one shipped, one restored) | [v1/](Qwen3.6-27B-AWQ-v1/) |
| Qwen3.6-27B-AWQ (no-think) | 7/10 done_signal | 1 runaway-generation, 2 operator-SIGTERM'd scroll-loops | [v2/](Qwen3.6-27B-AWQ-no-think-v2/), [v1-scroll-loop/](Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/), [v5-runaway-generation/](Qwen3.6-27B-AWQ-no-think-v5-runaway-generation/), [v8-scroll-loop/](Qwen3.6-27B-AWQ-no-think-v8-scroll-loop/) |

## Headline

**Coder-Next is unusable for this task class** — 0/10 ship at N=10, Wilson 95% [0%, 27.8%]. The failure mix shows two distinct mechanisms: workspace-hash stuck (5) and context-overflow (4). 27B variants both ship 7-8/10 but with different pathology profiles: thinking-mode has transient api_errors that retried successfully; no-think has scroll-loops requiring operator monitoring (or the new `tooling/scripts/check_substance.py`) to keep wall time bounded. **For internet-research workflows on local models, 27B is the only viable pick of the three.**

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families
- [`../findings-pairwise-quality-three-model.md`](../findings-pairwise-quality-three-model.md) — three-model quality study with hand-graded axes (only `p2_ci`, `p2_extract`, `p2_triage` graded so far; this cell deferred to follow-up)
- [`../../microbench-2026-04-28/market-research/`](../../microbench-2026-04-28/market-research/) — earlier N=3 entry with full per-model READMEs at the smaller sample size
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) — failure-mode definitions
