# doc-synthesis — Qwen3.6-27B-AWQ

**Run name:** `p3_doc_27b_v1` (1 of 3 — all 3 FAIL but for two distinct reasons; this is the cleanly-completed FAIL)
**Wall:** 8.1 minutes (487s), 33 iterations, finish via `done()` signal
**Cost upper:** $0.0106
**Verdict:** **FAIL** — captured 8/8 facts but went 765 words >700 limit

## Why this entry is here

This is the cleanly-completed run of three. v2 and v3 entered identical-call-loops on `brief.md` and were manually advanced — see `summary.json` for those runs in the source bench repo (`p3_doc_27b_v2`, `p3_doc_27b_v3`). All three runs hit 8/8 planted facts. The failure mode is consistent across the series: **the model can't compress to the 700-word limit**.

This is a *different* failure pattern than what the prior dreamserver-PR-audit benchmarks documented (where 27B's failure mode was no-ship of a structurally-required `verdict.md`). On this task, 27B ships — it produces `brief.md` + `key-facts.md` + research notes — and ships *with everything the planted-fact grader is looking for*. It just can't trim to 700 words.

The 27B failure is symmetric across the runs: 765, 775, 768 words. The model writes a complete brief with 8/8 facts captured and stops at "this is good content, around the right length, but ~70 words over." It doesn't have the trim-without-losing-fact-coverage skill on this task.

## What's in this folder

- [`brief.md`](deliverable/brief.md) — the executive brief (765 words, FAIL on word limit)
- [`key-facts.md`](deliverable/key-facts.md) — supporting fact-extraction file
- [`research/`](deliverable/research/) — agent's working notes
- [`decisions/`](deliverable/decisions/) — ADRs explaining recommendation framing
- [`README.md`](deliverable/README.md) — the agent's own readme
- [`grade.json`](grade.json) — facts captured + word count + the FAIL verdict
- [`label.json`](label.json) — `success-shipped-wrong`
- [`receipt.json`](receipt.json), [`summary.json`](summary.json), [`cost.json`](cost.json), [`transcript.jsonl`](transcript.jsonl)

## How to read this

Read `brief.md` first. It's a complete, well-organized executive brief on Nimbus Logistics — covers the ARR adjustment, the down-priced round, the customer concentration, the layoffs, the credit facility, the restructuring. Quality of analysis is high (all 8 planted facts surface naturally). The Recommendation section is clear and defensible.

Then read `grade.json`. It captured 8/8 facts (perfect coverage) and is 765 words (65 over the 700 limit, hence FAIL). The model didn't think this brief was too long; it stopped at iter 33 with a `done()` signal because, from its own perspective, the brief is the right length for the content.

For a deployment decision, the relevant question is: **does the consumer of this output need the 700-word limit?** If yes — say it feeds into a pipeline expecting the brief in a slide template with a max length — 27B's output is unusable as-is on this task class. If no, the 765-word brief is a useful artifact and the FAIL verdict is mostly a grader-vs-model calibration issue.

The Coder-Next entry next door [(`../Qwen3-Coder-Next-AWQ/`)](../Qwen3-Coder-Next-AWQ/) handled the trim more reliably (626 words, PASS). For tight-word-limit summary work specifically, Coder-Next is the pick.
