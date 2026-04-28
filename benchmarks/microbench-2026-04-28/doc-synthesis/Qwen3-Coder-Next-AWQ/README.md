# doc-synthesis — Qwen3-Coder-Next-AWQ

**Run name:** `p3_doc_coder_v1` (1 of 3 — v1 PASS, v2 went over word limit, v3 PASS = 2/3 PASS)
**Wall:** 0.6 minutes (39s), 13 iterations, finish via `done()` signal
**Cost upper:** $0.0008
**Verdict:** **PASS** — captured 8/8 facts at 626 words (within 700-word limit)

## Why this entry is here

This run is the cleanly-shipping case for Coder-Next on the doc-synthesis task. Useful as the comparison data for [the 27B entry next door](../Qwen3.6-27B-AWQ/) — same task, same input, same starter — Coder-Next compresses to a tight word limit while 27B doesn't.

Across N=3 attempts:
- v1 (this entry): 8/8 facts, 626 words → PASS
- v2: 7/8 facts, **1005 words** → FAIL (didn't try to compress)
- v3: 7/8 facts, within word limit → PASS

The v2 failure is a different failure mode than the v1/v3 pattern — for v2, the model didn't recognize the word limit at all. v1 and v3 produced acceptable-length output. **This is variance worth noting**: 2 of 3 runs PASS but the 1 failing run isn't a near-miss like 27B's; it's a "didn't apply the constraint" miss.

## What's in this folder

- [`brief.md`](deliverable/brief.md) — the executive brief (626 words, PASS on word limit)
- [`key-facts.md`](deliverable/key-facts.md) — supporting fact-extraction file
- [`research/`](deliverable/research/) — agent's working notes
- [`decisions/`](deliverable/decisions/) — ADRs
- [`README.md`](deliverable/README.md) — the agent's own readme
- [`grade.json`](grade.json) — fact coverage + word count + verdict
- [`label.json`](label.json) — `success-shipped`
- [`receipt.json`](receipt.json), [`summary.json`](summary.json), [`cost.json`](cost.json), [`transcript.jsonl`](transcript.jsonl)

## How to read this

The brief is a competent executive brief. Quality of writing is somewhat below the 27B run (more list-heavy, less narrative integration), but the 8 facts are all present and the recommendation is concrete. For a downstream consumer, this is usable output: 626 words is comfortably under the limit, the structure is clean, the citations are inline.

For deployment shape: if you want a tight-length business summary on a multi-source input, Coder-Next's $0.0008-per-attempt at ~1 minute wall is hard to beat. The 1/3 variance (v2 going 1005 words) means run-twice-and-pick-shorter is a cheap robustness improvement that costs ~$0.002 total.

For *high-stakes* business memos where the analysis quality matters more than the length compliance, 27B's 8/8 fact coverage at any length might be the safer default — pull the 27B output and have a human trim. The cost difference is real (~25× cheaper for Coder-Next) but the task-shape matters.
