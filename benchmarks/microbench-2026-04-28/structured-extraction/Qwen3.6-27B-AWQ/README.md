# structured extraction — Qwen3.6-27B-AWQ

**Run name:** `p2_extract_27b_v1` (1 of 3 — see [task family README](../README.md) for the full N=3 picture)
**Wall:** 71.0 s
**Cost upper:** $0.0015
**Verdict:** **PASS**

## Notes

**100% accuracy across all 20 fields, all 3 runs.** This is the kind of result you'd build a pipeline on. 1.2 min median wall, $0.0015 cost. The single sharpest accuracy demonstration in the entire microbench.

## Files

- [`grade.json`](grade.json) — verdict + per-dimension scores. Hand-graded subjective dimensions (where the grader has them) are filled in `hand_rating_placeholders` with `_GRADER_: claude-opus-4.7-1m-context`.
- [`cost.json`](cost.json) — wall, tokens, GPU, energy upper bound
- [`label.json`](label.json) — failure-mode classification per `tooling/FAILURE-TAXONOMY.md`
- [`summary.json`](summary.json) — finish reason, iteration count, total tokens
- [`receipt.json`](receipt.json) — vLLM args, harness git SHA, GPU snapshot

This is a lean entry. Transcripts and deliverable artifacts for this run live in the source bench repo at `agent-pilot/logs/p2_extract_27b_v1/`. The 3 highest-signal task families ([adversarial-hallucination](../../adversarial-hallucination/), [market-research](../../market-research/), [doc-synthesis](../../doc-synthesis/)) have full per-model entries with transcripts + deliverables; this one doesn't, to keep the repo size manageable. See [`../README.md`](../README.md) for the rationale.
