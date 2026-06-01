# Cross-model qualitative spot-grades (2026-05-31)

> **⚠️ Read this header before quoting anything below.** Every score here is a **provisional, single
> same-family LLM grade** (claude-opus-4-8), **N=1 representative run** per cell. It is **not validated**.
> Per [`tooling/QUALITATIVE-GRADING-PROTOCOL.md`](tooling/QUALITATIVE-GRADING-PROTOCOL.md), these
> load-bear *nothing* until a human or non-Claude grader confirms them. This doc exists to make the
> qualitative *direction* visible across models in one place — not to rank them.

## Why this doc exists
The aggregate microbench pass-rate is a **deceptive tie** (~7–8/12 across a 15× scale range). The
qualitative layer is where the real differentiation lives — but it was scored only on a few local-AWQ
cells. This pass extends provisional qualitative coverage to the **no-think arm** and the **big/varied-quant
models** (397B, MiniMax, 27B-FP8), and adds an **inter-rater** second opinion on the already-graded cells.
The point is the same one the binary tie hides: *models that "both PASS" can differ sharply in stance,
calibration, source-skepticism, and safety.*

## What got graded this pass
| Tier | Cells | Grade home |
|---|---|---|
| Inter-rater (reproducibility) | doc-synthesis, market-research, adv-hallucination | `hand_rating_2nd_grader` in each cell's grade.json (PRs #38, #40) |
| Tier A null-fill | business-memo, project-management (both models + no-think business) | `hand_rating_2nd_grader` in grade.json (PR-A) |
| Tier B no-think | doc / market / writing / pm (no published grade.json) | [`benchmarks/microbench-phase-b-2026-05-02/qualitative-no-think-spot-grades.json`](benchmarks/microbench-phase-b-2026-05-02/qualitative-no-think-spot-grades.json) |
| Tier D big models | 397B, MiniMax, 27B-FP8 on doc + business | `qualitative-spot-grades.json` in each hardware-tests entry |

## The cross-model picture (provisional)
**Business-memo (stance / calibration / fabrication) — the cell where the tie hides the most:**
- **27B-think** best *calibration* (separates hard facts from labeled inferences).
- **27B-no-think** best *balance* of correct-stance + brevity; nails the runway inconsistency + ARR gap.
- **Coder-Next** tightest/most-executive memo and the only one to catch the sign-off-skew signal — **but
  its memo misses the highest-severity planted signal (runway math)**. A "PASS" erases that.
- **397B / 27B-FP8** land HOLD with crisp change-conditions; **MiniMax** softens to "proceed-with-conditions"
  (lightest pushback) but adds cap-table/liq-pref insight the others miss.
- **Fabrication count is 0 across every model graded** — the shared strength.

**Doc-synthesis (source-skepticism / stance):** MiniMax and 27B-FP8 deliver clean PASS-with-conditions;
**397B uniquely hedges to "more diligence needed" — the one stance the task flags as weak.** The varied-quant
big models all land *inside* the 700-word limit where the 27B-AWQ baseline overran (perfect content, FAIL
on length) — an editorial-discipline difference, not a reasoning one.

**Safety (adversarial-hallucination):** 27B is flawless (0 dangerous confirmations); **Coder-Next confirms
a non-existent bug as real** — the exact failure this cell exists to catch. Same headline pass, opposite
safety profile.

**No-think arm:** graded uniformly excellent — **but see the calibration flag**: a uniform-5 pass is as
likely to mean "under-critical grader" as "uniformly excellent model." The honest read is "no obvious
qualitative regression vs think-mode on these synthesis tasks," not "no-think is a 5/5 model."

## Inter-rater reliability (the one hard check here)
Across the 3 full entries re-graded by an independent (same-family) pass: **~14/15 dim-scores reproduced**,
with **2 single-point divergences**, both on *under-specified rubric points* — `source_skepticism`
conflates source-reliability-eval with claim-skepticism, and the adv-hall "issue 009" citation rule is
ambiguous in the ground truth. So the qualitative layer reproduces well at the direction level; where it
wobbles, it's the **rubric** that's fuzzy, not the artifact. Recommended fix: split `source_skepticism`
into two dims and tighten the 009 rule.

## What this still is NOT
- **Not a ranking.** No uniform rubric spans cloud + local; the cloud models (Opus/GPT-5.5) are
  ungraded on these axes (and can't be Claude-graded — grader-independence).
- **Not validated.** One same-family grader, N=1. The next real step is a human/non-Claude pass and N>1
  on the divergent cells.
- **Not full-N.** Scoped to representatives (disclosed in each file), not every replicate.

See [`MICROBENCH-INDEX.md`](MICROBENCH-INDEX.md) for the model roster and the four-"27B" disambiguation.
