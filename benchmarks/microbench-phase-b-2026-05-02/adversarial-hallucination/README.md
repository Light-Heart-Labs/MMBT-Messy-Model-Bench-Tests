# Adversarial hallucination

> Classify 15 issues (6 real / 9 fabricated) — resistance to confident-but-wrong claims.

## Results — N=10 for `27b-nothink`; N=3 or N=10 for thinking/Coder per `microbench-2026-04-28`

| Model | done_signal ship rate |
|---|---:|
| Qwen3-Coder-Next-AWQ | 5/10 |
| Qwen3.6-27B-AWQ (thinking) | 7/10 |
| **Qwen3.6-27B-AWQ (no-think)** | **10/10** |

> † See [`../findings.md`](../findings.md) § "Per-cell results" — N=3 baselines on this cell used an older harness sha; cross-batch comparisons may include harness-drift effects.

> ★ Two additional `p3_market` 27B-no-think runs were operator-SIGTERM'd at >30 identical-template iters per the documented methodology rule. Including them: 7/10. See [`./Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/`](./Qwen3.6-27B-AWQ-no-think-v1-scroll-loop/), [`./Qwen3.6-27B-AWQ-no-think-v8-scroll-loop/`](./Qwen3.6-27B-AWQ-no-think-v8-scroll-loop/), and [`./Qwen3.6-27B-AWQ-no-think-v5-runaway-generation/`](./Qwen3.6-27B-AWQ-no-think-v5-runaway-generation/).

## Cross-references

- [`../findings.md`](../findings.md) — task-family discussion in context with other 11 task families (the cross-cutting writeup)
- [`microbench-2026-04-28/adversarial-hallucination/`](../../microbench-2026-04-28/adversarial-hallucination/) — earlier N=3 entry; this drop expands sample size and adds the no-think arm
- [`../../../tooling/tasks/task_hallucination.md`](../../../tooling/tasks/) — the task spec
