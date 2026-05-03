# Failure-mode entry

This folder is a **failure-mode entry** — the model produced **zero artifacts** on the single-PR audit task (the floor of the escalation ladder). The folder is preserved because "this model can't even start" is itself a deployment-relevant property.

**Model**: Qwen3.6-35B-A3B-AWQ (4-bit AWQ, MoE thinking)
**Task**: [`task_pr_audit_n1.md`](../../../tooling/tasks/task_pr_audit_n1.md)
**Outcome**: 0 / 1 artifacts produced; model investigated for 28 iters then stopped without writing
**Wall**: 1.7 min
**Failure label**: `floor-failure` (per [`tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md))

## Why this entry matters

The 1-PR audit is the simplest task in the escalation ladder (1 → 2 → 4 → 8 → 16 → 32 PRs). If a model can't ship at the floor, it won't ship at any higher complexity. Both other models on this benchmark — Coder-Next (1/3 correct) and 27B (0/3 spec-compliant but 3/3 implicit-correct in `review.md`) — at least produced *something*. 35B-A3B-AWQ at 4-bit didn't clear the floor.

Higher-precision quantizations (FP8, BF16) might fare better; this entry only tests 4-bit AWQ.

## How to read this entry

Start with [`README.md`](README.md). The receipts ([`receipt.json`](receipt.json), [`cost.json`](cost.json), [`label.json`](label.json), [`transcript.jsonl`](transcript.jsonl)) document the run end-to-end; there's no deliverable to drill into.

For the broader context, see [`COMPARISON.md`](../../../COMPARISON.md).
