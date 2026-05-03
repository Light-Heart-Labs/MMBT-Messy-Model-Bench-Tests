# Failure-mode entry

This folder is a **failure-mode entry** — the model produced **no audit deliverable** across 5 attempts on the 75-PR audit task. The folder is preserved because the *kinds* of failure are themselves the comparison data.

**Model**: Qwen3-Coder-Next-AWQ (4-bit AWQ, MoE 80B/3B-active)
**Task**: [`task_dreamserver_pr_audit.md`](../../../tooling/tasks/task_dreamserver_pr_audit.md)
**Outcome**: 0 / 5 attempts shipped a deliverable

## Failure shapes observed (3 distinct)

1. `identical-call-loop` — same tool template repeated until the harness stuck-detector fired
2. `cyclic-name-slop` — model cycled through PR numbers without writing artifacts
3. `stuck-in-research` — model read PRs and took notes inside the transcript but never moved to the "produce verdict.md" stage

## How to read this entry

Start with [`README.md`](README.md) for the full failure analysis and per-attempt receipts. Then [`tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) for the failure-mode vocabulary used here.

For the comparison context this entry contributes to, see [`COMPARISON.md`](../../../COMPARISON.md) § "Long-horizon (dreamserver) — where the agentic regime breaks".
