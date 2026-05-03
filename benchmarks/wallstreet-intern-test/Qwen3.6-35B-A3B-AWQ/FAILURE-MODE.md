# Failure-mode entry

This folder is a **failure-mode entry** — **0 of 3 attempts** produced a usable investment-memo deliverable. The folder is preserved as failure-mode evidence consistent with the model's [floor failure on the 1-PR audit](../../dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/).

**Model**: Qwen3.6-35B-A3B-AWQ (4-bit AWQ, MoE thinking)
**Task**: [`task_investment_memo.md`](../../../tooling/tasks/task_investment_memo.md)
**Outcome**: 0 / 3 attempts shipped
**Wall**: 0.2–7 min per attempt
**Failure mix**: `floor-failure` / `api-error` / `stuck-in-research`

## How to read this entry

Start with [`README.md`](README.md) for the per-attempt summaries and receipts.

For the broader pattern (this model is below the floor at 4-bit AWQ for these task classes), see [`COMPARISON.md`](../../../COMPARISON.md). For the failure-mode vocabulary, see [`tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md).
