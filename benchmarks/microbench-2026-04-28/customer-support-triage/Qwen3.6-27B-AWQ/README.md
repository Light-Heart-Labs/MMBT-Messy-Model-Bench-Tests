# customer support triage — Qwen3.6-27B-AWQ

**Run name:** `p2_triage_27b_v1` (1 of 3 — see [task family README](../README.md) for the full N=3 picture)
**Wall:** 196.1 s
**Cost upper:** $0.0043
**Verdict:** **PASS**

## Notes

86.7% category accuracy, 100% duplicate-cluster recall every run. 3.3 min median wall.

## Files

- [`grade.json`](grade.json) — verdict + per-dimension scores. Hand-graded subjective dimensions (where the grader has them) are filled in `hand_rating_placeholders` with `_GRADER_: claude-opus-4.7-1m-context`.
- [`cost.json`](cost.json) — wall, tokens, GPU, energy upper bound
- [`label.json`](label.json) — failure-mode classification per `tooling/FAILURE-TAXONOMY.md`
- [`summary.json`](summary.json) — finish reason, iteration count, total tokens
- [`receipt.json`](receipt.json) — vLLM args, harness git SHA, GPU snapshot

This is a lean entry. The transcript and deliverable artifacts for this specific run aren't mirrored in MMBT (lean entry — saves repo space). But the task prompt, input starter, ground truth, and grader script for this task family are all in [`../../../../tooling/`](../../../../tooling/) — with those + your own GPU you can rerun this task family at N=3 yourself. The original bench-side run name was `p2_triage_27b_v1`. The 3 highest-signal task families ([adversarial-hallucination](../../adversarial-hallucination/), [market-research](../../market-research/), [doc-synthesis](../../doc-synthesis/)) have full per-model entries with transcripts + deliverables; this one doesn't, to keep the repo size manageable. See [`../README.md`](../README.md) for the rationale.
