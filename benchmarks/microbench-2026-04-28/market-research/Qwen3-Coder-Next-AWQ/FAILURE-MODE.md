# Failure-mode entry

This folder is a **failure-mode entry** — `STRUCTURAL_FAIL` on all 3 attempts (no `recommendation.md`, `comparison.md`, or `sources.md` produced). The folder is preserved because the failure shape is the comparison data — Coder-Next can't drive the kind of multi-step internet-research workflow that 27B drives.

**Model**: Qwen3-Coder-Next-AWQ (4-bit AWQ, MoE 80B/3B-active)
**Task**: [`task_market_research.md`](../../../../tooling/tasks/task_market_research.md)
**Outcome**: 0 / 3 attempts shipped a structured deliverable
**Wall**: ~25 min (stuck-detector eventually fired)
**Failure label**: `stuck-in-research` (per [`tooling/FAILURE-TAXONOMY.md`](../../../../tooling/FAILURE-TAXONOMY.md))

## What this contributes to the comparison

This is one of the two **sharpest local-model superiority signals** in the repo (the other being `adversarial-hallucination`):

- 27B (this same task, [sibling entry](../Qwen3.6-27B-AWQ/)): 3/3 STRUCTURAL_PASS, 12-18 inline cites, 29-33 distinct URLs
- Coder-Next (this entry): 0/3 STRUCTURAL_FAIL

Confirmed reproducible at N=10 in [`microbench-phase-b-2026-05-02`](../../../microbench-phase-b-2026-05-02/) — Coder-Next 0/10, Wilson 95% [0%, 27.8%].

## How to read this entry

Start with [`README.md`](README.md). The transcript is the most useful artifact for understanding the failure — the agent reads pages, takes notes inside the transcript, but never moves to the "produce structured deliverables" stage.

For the comparison context, see [`COMPARISON.md`](../../../../COMPARISON.md) § "I need internet research with cited sources".
