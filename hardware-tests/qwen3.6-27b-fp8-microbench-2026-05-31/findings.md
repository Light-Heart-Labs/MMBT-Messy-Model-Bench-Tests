# Qwen3.6-27B (dense, FP8) on 2× RTX PRO 6000 Blackwell — microbench N=5

> **⚠️ IN-PROGRESS CAPTURE (as of 2026-05-31).** The think-mode p3 tail is still running
> (`p3_market` v4–v5, `p3_writing`, and the `p3_pm` think reps are landing). Numbers below are a
> **snapshot**; no-think is complete (60/60 cells), think is partial (54 cells graded so far).
> This doc is committed now to preserve the data + qualitative analysis; it will be finalized when
> the grid completes. Hand-grading dimensions (stance/calibration/fabrication) are not yet filled.

Qwen3.6-27B dense, served as **FP8 on vLLM**, run through the full MMBT 12-family agentic microbench at
**N=5** per cell, in both **`--thinking on` and `--thinking off`** modes. Same Tower2 rig and harness as
the [397B vs Step-3.7-Flash entry](../qwen3.5-397b-vs-step3.7-flash-2026-05-29/).

## Why this run exists — it replaces an excluded serving failure

The [397B entry](../qwen3.5-397b-vs-step3.7-flash-2026-05-29/findings.md) notes that fresh **Q8/FP8**
runs of Qwen3.6-27B were attempted and **excluded as serving failures** ("27B-Q8: 23/36 token-runaway +
8/36 HTTP-400, only 4 clean — excluded, not shown"). **This FP8 run is the clean redo:** across
**112 completed cells, 0 token-runaways and 0 HTTP-400 storms** — the model completes the agent loop
normally. *FP8 on Blackwell SM120 is a viable serving path for this model where the earlier Q8 attempt
was not.* That alone closes the gap the published entry flagged.

## Headline finding — thinking is **net-negative** for 27B on this bench

| | no-think | think (partial) |
|---|---|---|
| **Aggregate** | **35/60 (58%)** | 26/54 so far (trending lower) |

No-think aggregate-ties the field's ~7–8/12 band (same 58% as MiniMax-M2.7, near 397B-no-think). Think
mode is **worse**, and the divergence is mechanistic, not noise:

- **The smoking gun — `p2_triage`: 0/5 think vs 5/5 no-think.** Closed-vocabulary customer-support
  classification. Both modes spend the *same* ~10–14 iterations and ~7.2k tokens — but thinking makes the
  model **reason its way off the fixed label set**, and it fails every replicate. No-think answers from the
  vocabulary and passes every replicate. This is the cleanest "overthinking breaks a bounded task" result
  in the run.
- **Thinking *helps* exactly one task: `p3_business` (5/5 think vs 1/5 no-think).** Here the extra
  reasoning trims the memo to fit the 700-word cap; no-think busts the cap (perfect content, FAIL on
  length — see qualitative). So thinking's one win is *length discipline*, not insight.
- **Thinking hurts the rest of p3** (doc, market) on the same word-limit/variance axes.

**Net: ship 27B-FP8 in no-think for this workload.** Thinking buys a length-discipline win on one task and
loses a classification task outright.

## Scorecard (PASS = grader verdict; majority ≥3/5 ✓). Q4/Coder refs from microbench-2026-04-28.

| family | no-think | think | iter_med (nt/th) | tok_med (nt/th) | 27B-Q4 ref | note |
|---|---|---|---|---|---|---|
| p1_bugfix | **5/5** ✓ | **5/5** ✓ | 153 / 89 | 34.3k / 30.9k | 3/3 | fixes planted bugs cleanly |
| p1_testwrite | 0/5 | 0/5 | 88 / 53 | 36.0k / 42.8k | 0/3 † | † starter-code task-design issue |
| p1_refactor | 0/5 | 0/5 | 86 / 61 | 10.7k / 12.8k | 0/3 † | † starter-code task-design issue |
| p2_extract | **5/5** ✓ | **5/5** ✓ | 7 / 6 | 3.1k / 3.4k | 3/3 | fast, clean |
| p2_ci | **5/5** ✓ | **5/5** ✓ | 31 / 28 | 4.7k / 6.9k | 3/3 | |
| p2_hallucination | **5/5** ✓ | **5/5** ✓ | 20 / 15 | 5.6k / 6.8k | 3/3 | |
| p2_triage | **5/5** ✓ | **0/5** ✗ | 14 / 10 | 7.2k / 7.3k | 3/3 | **think breaks it** |
| p3_doc | 1/5 | 0/5 | 24 / 28 | 9.4k / 13.0k | 0/3 | word-cap grader artifact (below) |
| p3_business | 1/5 | **5/5** ✓ | 43 / 32 | 23.6k / 21.8k | 2/3 | **think wins on length discipline** |
| p3_market | 3/5 ✓* | 1/4* | 136 / 196 | 41.6k / 59.3k | 3/3* | *STRUCTURAL_PASS; high variance |
| p3_writing | **5/5** ✓ | *(pending)* | 23 / — | 7.4k / — | 0/3 | big gain vs Q4 (0/3) |
| p3_pm | 0/5 | 0/5 | 14 / 10 | 4.6k / 4.0k | 0/3 | genuine weak spot |

`†` test-writing/refactoring are affected by a known starter-code task-design issue (see repo
KNOWN-LIMITATIONS.md), not a model capability gap — same caveat as every other model in the bench.
`*` market-research is graded STRUCTURAL_PASS; citation validity is a hand-grading dimension.

## Qualitative — behavioral texture (sourced from graded transcripts + deliverables)

These cover the p3 longform tasks where I read the actual artifacts across the field. **27B is the
content winner held back by format discipline and variance.**

- **Business (bias detection) — best in the field.** 27B is the only dense model to sweep **8/8 planted
  signals**, and the only one to reliably catch the soft traps (build-vs-buy, sign-off skew) that
  **397B-think misses (5/8)**. Derives every number cleanly, zero fabricated figures. A 27B model
  out-recalling a 397B model on the same rubric is a real result, not a speed asterisk.
- **Doc (synthesis) — sharpest prose, loses on a grader artifact.** 27B's tension-framing ("it's not
  growing its way to profitability, it's cutting its way there") is the most decisive in the field, with
  the best epistemic calibration (tags each claim as recollected/forward-looking/unverified). But it
  **fails the word cap** because the grader counts markdown scaffolding (`[Source N]`, `**`, `---`, table
  pipes) as words — 27B's citation-dense style is ~697 prose words by `wc -w` but ~711 by the grader.
  **The content winner is a pass/fail loser on a counting artifact** — flagged for a grader fix before
  these pass-rates are quoted.
- **Market (research) — best citation honesty, worst variance.** 27B's `sources.md` is the strongest
  provenance trail of any model (real URLs with honest extraction caveats; flags what it *couldn't* fetch
  rather than inventing it — cleaner than 397B's empty-hash "verification"). But reliability is weak: only
  ~half the reps converge; failures are heavy **JS-pricing scrape-loops** (one think rep was
  operator-killed after 22+ byte-identical Bitwarden-scrape calls — recorded as a dropped-stuck rep, see
  caveats).
- **Failure signature: stall, not runaway.** Consistent with the published 27B-Q4 finding — 27B's misses
  are quiet (word-cap busts, scrape-loops, pm under-delivery), never the over-generation runaways that
  Coder-Next/Flash/MiniMax(@temp0.3) show.

## Caveats (read with the numbers)

- **Run in progress.** Think-mode p3 tail (`p3_market` v4–v5, `p3_writing`, `p3_pm`) is still landing.
  Think aggregate (26/54) will move; no-think (35/60) is final.
- **`p3_market_27b-fp8-think_v3` dropped.** Operator-SIGTERM'd mid-run after a degenerate JS-scrape
  repetition loop (22+ byte-identical tool calls; `--stuck-threshold 500` would not have caught it for
  hundreds more iterations). Recorded as a dropped-stuck rep, not retried — market-think tops out at 4/5.
- **Hand-grading dimensions not yet filled** (stance correctness, calibration, fabrication count). The
  qualitative section above is my close reading of the artifacts, not finalized human grades.
- **`†` p1_testwrite/refactor** task-design issue applies to all models; not a 27B-specific failure.
- **Q4/Coder reference columns are N=1–3** from a prior run on an older grader — directional only.

## Reproduce

```bash
# FP8 served on vLLM (one engine per GPU; ports 8001/8002 used for the two thinking modes).
# Run the full 12-family microbench at N=5, both modes (mode encoded in the label):
bash tooling/scripts/run_microbench.sh qwen3.6-27b-fp8 8001 27b-fp8-nothink 5 "" off 131072
bash tooling/scripts/run_microbench.sh qwen3.6-27b-fp8 8002 27b-fp8-think   5 "" on  131072
bash tooling/scripts/grade_microbench.sh 27b-fp8-nothink
bash tooling/scripts/grade_microbench.sh 27b-fp8-think
bash tooling/scripts/summarize.sh 27b-fp8-nothink
```
