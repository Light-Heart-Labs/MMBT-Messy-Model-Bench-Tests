# Qwen3.6-27B (dense, FP8) on 2× RTX PRO 6000 Blackwell — microbench N=5, think vs no-think

Qwen3.6-27B dense, served as **FP8 on vLLM** (one engine per GPU, sm_120, driver 595.58.03), run
through the full MMBT 12-family agentic microbench at **N=5** per cell in both `--thinking on` and
`--thinking off` modes. Same Tower2 rig and harness as the
[397B vs Step-3.7-Flash entry](../qwen3.5-397b-vs-step3.7-flash-2026-05-29/).

**120 cells attempted, 119 graded** (one think cell dropped — see caveats). Hand-grading dimensions
(stance/calibration/fabrication) are not filled; the qualitative section below is close reading of the
graded transcripts/artifacts, not finalized human grades.

## Why this run exists — it replaces an excluded serving failure

The [397B entry](../qwen3.5-397b-vs-step3.7-flash-2026-05-29/findings.md) notes that fresh **Q8/FP8**
runs of Qwen3.6-27B were attempted and **excluded as serving failures** ("27B-Q8: 23/36 token-runaway +
8/36 HTTP-400, only 4 clean — excluded, not shown"). **This FP8 run is the clean redo, and FP8 serving
is stable** where Q8 was not:

| | clean `done_signal` | error finish-reasons |
|---|---|---|
| excluded **Q8** attempt | 4/36 | **23/36 token-runaway + 8/36 HTTP-400** (a serving-instability storm) |
| this **FP8** run | **113/119** | 6: **5 HTTP-400 + 1 max_tokens runaway** |

The honest distinction: the **6 FP8 errors are not quant instability — they are the model looping
*itself* into the context ceiling on the two hardest tasks.** All 6 are deep-iteration cells:
`p3_market` (research loops) and `p3_business`-think (e.g. v2 errored at **iter 186 / 12M cumulative
prompt-tokens** — it kept issuing tool calls until the request exceeded the 131072 window). That is a
model-behavior failure mode, not the FP8 weights misbehaving. **FP8 on Blackwell SM120 is a viable
serving path for this model** — which closes the gap the published 397B entry flagged.

## Headline finding — thinking is **net-negative** for 27B on this bench

| | no-think | think |
|---|---|---|
| **Aggregate** | **35/60 (58%)** | **29/60 (48%)** |

No-think aggregate-ties the field's ~7–8/12 band (same 58% as MiniMax-M2.7, near 397B-no-think). Think
mode is **6 cells worse**, and the divergence is mechanistic, not noise:

- **The smoking gun — `p2_triage`: 0/5 think vs 5/5 no-think.** Closed-vocabulary customer-support
  classification. Both modes spend the *same* ~10–14 iterations and ~7.2k tokens — but thinking makes the
  model **reason its way off the fixed label set** and it fails every replicate; no-think answers from the
  vocabulary and passes every replicate. The cleanest "overthinking breaks a bounded task" result here.
- **`p3_writing`: 1/5 think vs 5/5 no-think.** A 3-audience rewrite with length limits — thinking
  over-produces and busts the constraints; no-think respects them.
- **Thinking *helps* exactly one task: `p3_business` (5/5 think vs 1/5 no-think)** — and that win is
  *length discipline*, not insight: the extra reasoning trims the memo to the 700-word cap, which no-think
  busts (perfect content, FAIL on length — see qualitative).

**Net: ship 27B-FP8 in no-think for this workload.** Thinking buys one length-discipline win and loses a
classification task and a writing task outright.

## Scorecard (PASS = grader verdict, majority ≥3/5 ✓). Q4/Coder refs from microbench-2026-04-28 (N=1–3).

| family | no-think | think | iter_med (nt/th) | tok_med (nt/th) | 27B-Q4 ref | note |
|---|---|---|---|---|---|---|
| p1_bugfix | **5/5** ✓ | **5/5** ✓ | 153 / 89 | 34.3k / 30.9k | 3/3 | fixes planted bugs cleanly |
| p1_testwrite | 0/5 | 0/5 | 88 / 53 | 36.0k / 42.8k | 0/3 † | † starter-code task-design issue |
| p1_refactor | 0/5 | 0/5 | 86 / 61 | 10.7k / 12.8k | 0/3 † | † starter-code task-design issue |
| p2_extract | **5/5** ✓ | **5/5** ✓ | 7 / 6 | 3.1k / 3.4k | 3/3 | fast, clean |
| p2_ci | **5/5** ✓ | **5/5** ✓ | 31 / 28 | 4.7k / 6.9k | 3/3 | |
| p2_hallucination | **5/5** ✓ | **5/5** ✓ | 20 / 15 | 5.6k / 6.8k | 3/3 | |
| p2_triage | **5/5** ✓ | **0/5** ✗ | 14 / 10 | 7.2k / 7.3k | 3/3 | **think breaks it** |
| p3_doc | 1/5 | 0/5 | 24 / 28 | 9.4k / 13.0k | 0/3 | word-cap (artifact — below) |
| p3_business | 1/5 | **5/5** ✓ | 43 / 32 | 23.6k / 21.8k | 2/3 | **think wins on length discipline** |
| p3_market | 3/5 ✓* | 3/4 ✓* | 136 / 61 | 41.6k / 32.2k | 3/3* | *STRUCTURAL_PASS; v3 dropped (think) |
| p3_writing | **5/5** ✓ | 1/5 | 23 / 19 | 7.4k / 6.4k | 0/3 | **think breaks it; big gain vs Q4** |
| p3_pm | 0/5 | 0/5 | 14 / 10 | 4.6k / 4.0k | 0/3 | genuine weak spot, both modes |

`†` test-writing/refactoring are affected by a known starter-code task-design issue (repo
KNOWN-LIMITATIONS.md), not a model capability gap — same caveat as every model in the bench.
`*` market-research is graded STRUCTURAL_PASS (files + 5 products + pricing + 50-seat math + citations);
citation validity is a hand-grading dimension.

## Qualitative — behavioral texture (sourced from graded transcripts + deliverables)

27B is the **content winner** on the p3 longform tasks, held back by **format discipline** and
**variance**.

- **Business (bias detection) — best in the field.** 27B is the only dense model to sweep **8/8 planted
  signals** (verified in grade.json `signal_hits`), and the only one to reliably catch the soft traps
  (build-vs-buy, sign-off skew) that **397B-think misses (5/8)**. Derives every number cleanly, zero
  fabricated figures. A 27B model out-recalling a 397B model on the same rubric is a real result.
- **Doc (synthesis) — sharpest prose, loses on a near-miss word cap.** 27B's tension-framing ("it's not
  growing its way to profitability, it's cutting its way there") is the most decisive in the field, with
  the best epistemic calibration (tags each claim as recollected/forward-looking/unverified). It fails the
  cap by a hair: the briefs run **~700 words by `wc -w` but the grader counts 703–705** (markdown
  scaffolding — `[Source N]`, `**`, table pipes — inflates the count just past 700). Real verbosity is
  marginal; the FAIL is mostly a counting boundary. *Flagged for a grader fix before quoting doc
  pass-rates.*
- **Market (research) — best citation honesty, worst variance.** 27B's `sources.md` is the strongest
  provenance trail of any model (real URLs with honest extraction caveats; it flags what it *couldn't*
  fetch rather than inventing it — cleaner than 397B's empty-hash "verification"). But reliability is
  weak: failures are heavy **JS-pricing scrape-loops** (the dropped think rep, v3, was operator-killed
  after 20+ byte-identical Playwright/Bitwarden scrape calls; a no-think rep, v4, hit the max_tokens cap
  the same way).
- **Failure signature: stall / loop-into-ctx, not runaway.** Consistent with the published 27B-Q4
  finding — 27B's misses are quiet (word-cap busts, scrape-loops, pm under-delivery, the 6 ctx-overflow
  errors), never gratuitous over-generation across the board.

## Caveats (read with the numbers)

- **`p3_market_27b-fp8-think_v3` dropped (think market is 3/4, not /5).** Operator-SIGTERM'd across three
  attempts, each a degenerate JS-scrape repetition loop (`--stuck-threshold 500` would not catch it for
  hundreds more iterations). Recorded as a dropped-stuck rep, not retried. See `market_v3.skip-reason`.
- **6 error-finish cells** (`p3_business` nt-v3 / th-v2 / th-v5; `p3_market` nt-v2 / nt-v4 / th-v1): 5
  HTTP-400 (context-overflow from deep tool-loops) + 1 max_tokens runaway. They are graded FAIL where the
  task is gradeable; they are *behavioral*, not FP8-serving, failures (see "Why this run exists").
- **Hand-grading dimensions not yet filled** (stance correctness, calibration, fabrication count). The
  qualitative section is close reading, not finalized human grades.
- **`†` p1_testwrite/refactor** task-design issue applies to all models; not a 27B-specific failure.
- **Q4/Coder reference columns are N=1–3** from a prior run on an older grader — directional only.

## Reproduce

```bash
# FP8 served on vLLM, one engine per GPU (ports 8001 / 8002 for the two thinking modes, run concurrently).
bash tooling/scripts/run_microbench.sh qwen3.6-27b-fp8 8001 27b-fp8-nothink 5 "" off 131072
bash tooling/scripts/run_microbench.sh qwen3.6-27b-fp8 8002 27b-fp8-think   5 "" on  131072
bash tooling/scripts/grade_microbench.sh 27b-fp8-nothink
bash tooling/scripts/grade_microbench.sh 27b-fp8-think
bash tooling/scripts/summarize.sh 27b-fp8-nothink
```

See [`manifest.json`](manifest.json) for serving config, image digest, and run inventory.
