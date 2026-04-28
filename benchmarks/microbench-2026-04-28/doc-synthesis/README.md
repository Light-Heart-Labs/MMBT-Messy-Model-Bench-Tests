# doc-synthesis

> Agent reads 5 documents about a fictional company (Nimbus Logistics, Inc.) — mix of press release, leaked board memo, internal Slack export, customer-facing blog, employee blog — and writes a 1-page executive brief for a follow-on investment decision. Brief must be ≤700 words and capture material facts that don't appear in the press release surface narrative.
>
> **Pass criteria** (programmatic): captures ≥6 of 8 planted material facts, brief is ≤700 words. (Word limit is the hard constraint.)

## Why this task

Two things this task tests in tension:
1. **Multi-source fact extraction** — the 8 planted facts aren't all in one source. Some are in the press release, some require reading the leaked memo, some require connecting Slack-export comments to the official narrative.
2. **Brevity under a hard length cap** — 700 words is shorter than the natural length of a "complete" executive brief on a complex situation. The agent has to be selective about what makes the cut.

Most agents that do well on (1) struggle with (2): they capture all the facts and then can't compress to the limit. That trade-off is exactly what the results show.

## Results — N=3 per model

| Model | PASS | Facts captured (median) | Word count (median) | Wall (median) | Failure mode |
|---|---|---|---|---|---|
| **[Qwen3.6-27B-AWQ](Qwen3.6-27B-AWQ/)** | **0/3** | 8/8 every run | 768 (range 765-775) | 32.7 min ‡ | word-limit-trim failure; v2/v3 entered identical-call-loops on `brief.md` |
| **[Qwen3-Coder-Next-AWQ](Qwen3-Coder-Next-AWQ/)** | 2/3 | 7/8 (v1: 8/8, v2: 7/8, v3: 7/8) | 626 (range 626-1005; v2 went over) | 0.6 min | v2 went 1005 words >700 |

‡ 27B median wall is dominated by v2 (135 min, wall_killed) and v3 (33 min, wall_killed). The cleanly-completed v1 was 8 min.

The 27B failure shape is well-defined and worth describing in detail because it's the kind of pattern external readers should know to watch for:

1. v1: agent finishes via `done()` at iter 33 with 765-word brief. PASS on facts (8/8) but FAIL on word limit. 8 minutes.
2. v2: agent enters identical-call-loop. Writes `brief.md` with 763-word content, the harness reports the file write, the agent re-writes the same 763-word content. ~138 iters of identical writes before manual SIGTERM at iter 159. Workspace state hash unchanged → would have eventually triggered the 500-iter stuck-detector at ~5 hours wall. The model never produced a different word count because it appears to interpret "trim" as "rewrite the same content again."
3. v3: same pattern as v2. 58 same-content writes of `brief.md` (768 words). Killed at iter 71.

This pattern *only* shows up on the doc-synthesis task in the microbench. On business-memo (similar shape, 700-word limit) the same model managed 656 words on 2/3 runs and 708 words (1 over) on the third — the trim mostly worked. The failure correlate appears to be how much information the agent has to *remove* to hit the limit, not the limit itself. On doc-synthesis there's a lot to remove and the model can't decide what.

The Coder-Next runs handled the trim more reliably — 2/3 PASS at 626 words. The v2 run that went 1005 words is a different failure mode (didn't try to compress at all).

## Cross-references

- [`../findings.md`](../findings.md) § "27B has a documented word-limit-trim failure"
- [`../../../tooling/FAILURE-TAXONOMY.md`](../../../tooling/FAILURE-TAXONOMY.md) § identical-call-loop, success-shipped-wrong, wall-killed

## Task starter

The 5 source documents and the planted-fact list are in [`../../../tooling/inputs/phase3_doc_synthesis/sources.md`](../../../tooling/inputs/phase3_doc_synthesis/sources.md). Ground truth (the 8 specific facts and how each is canonically expressed) is in [`../../../tooling/graders/ground_truth/phase3_doc_synthesis.json`](../../../tooling/graders/ground_truth/phase3_doc_synthesis.json) — kept SEPARATE from `tooling/inputs/` (which is what the agent mounts) so the planted answers can't leak.
