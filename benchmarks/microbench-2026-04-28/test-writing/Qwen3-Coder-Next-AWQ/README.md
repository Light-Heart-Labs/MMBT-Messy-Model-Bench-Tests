# test writing — Qwen3-Coder-Next-AWQ

**Run name:** `p1_testwrite_coder_v1` (1 of 3 — see [task family README](../README.md) for the full N=3 picture)
**Wall:** 1396.1 s
**Cost upper:** $0.0303
**Verdict:** **FAIL**

## Notes

Same task-design issue affects Coder-Next identically.

## Files

- [`grade.json`](grade.json) — verdict + per-dimension scores. Hand-graded subjective dimensions (where the grader has them) are filled in `hand_rating_placeholders` with `_GRADER_: claude-opus-4.7-1m-context`.
- [`cost.json`](cost.json) — wall, tokens, GPU, energy upper bound
- [`label.json`](label.json) — failure-mode classification per `tooling/FAILURE-TAXONOMY.md`
- [`summary.json`](summary.json) — finish reason, iteration count, total tokens
- [`receipt.json`](receipt.json) — vLLM args, harness git SHA, GPU snapshot

This is a lean entry. Transcripts and deliverable artifacts for this run live in the source bench repo at `agent-pilot/logs/p1_testwrite_coder_v1/`. The 3 highest-signal task families ([adversarial-hallucination](../../adversarial-hallucination/), [market-research](../../market-research/), [doc-synthesis](../../doc-synthesis/)) have full per-model entries with transcripts + deliverables; this one doesn't, to keep the repo size manageable. See [`../README.md`](../README.md) for the rationale.
