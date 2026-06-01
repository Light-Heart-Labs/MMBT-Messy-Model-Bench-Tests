# Qualitative grading protocol

How MMBT's subjective (hand-rating) dimensions are scored, and the rules that keep them honest. This
exists because the qualitative layer is the most *valuable* part of the corpus (it explains the per-task
differences that the aggregate pass-rate washes into a deceptive "tie") **and** its least statistically
grounded part (N=1, single LLM grader). These rules bound that fragility.

## The dimensions
Subjective dims live in each cell's `grade.json` under `hand_rating_placeholders` (primary) and, where a
second pass exists, `hand_rating_2nd_grader`. They are 1–5 quality scores (prose, stance, skepticism,
tone, calibration, structure…), plus integer counts (`fabrication_count`, owner-accuracy, etc.). The
programmatic verdict (PASS/FAIL/STRUCTURAL_PASS) is separate and does **not** depend on these.

## Grader-independence requirement (the load-bearing rule)
1. **A grader must not be a benchmarked subject in the same comparison.** Claude (Opus) is a benchmarked
   model in the cloud entries (75-PR audit, wallstreet) — so **Claude cannot grade the Opus cloud entries**,
   and cross-model qualitative tables spanning cloud+local cannot be Claude-graded end-to-end. Open models
   (Qwen / MiniMax / StepFun) have no such conflict with a Claude grader.
2. **Single-grader scores are `provisional` at best.** One LLM pass is not validated. Promotion toward
   `strong` requires (a) a second *independent* grader, ideally human or non-Claude, and (b) N>1.
3. **Same-family second graders count for little.** An opus-4.8 re-grade of opus-4.7 scores (see the
   inter-rater PRs) tests reproducibility but is weak evidence of *correctness* — both share training
   lineage and likely failure modes.
4. **Label every score** with `_GRADER_`, `_GRADED_AT_`, and a `_NOTE_`/caveat. Never present an LLM
   qualitative score as validated.

## Why this matters (proven fragility)
The original 2026-04-28 pairwise study scored `p2_ci` with the regression attributed to the **wrong
model** (it read the CHANGELOG backwards); the error stood until a re-read. N=1 single-grader qualitative
is fragile enough to invert a verdict. The inter-rater passes (PR #38, #40) are the standing check against
this — and they already surfaced two single-point divergences clustering on *under-specified rubric
dimensions* (e.g. `source_skepticism` conflates "evaluates source reliability" with "skeptical of input
claims" → recommend splitting it).

## Status convention for null dims
A `null` qualitative field is ambiguous in bulk scans. Disambiguate:
- **`not_applicable`** — no deliverable to grade (e.g. a STRUCTURAL_FAIL cell that shipped no artifact).
  The existing `rater_notes` already says this on those cells; treat their nulls as N/A, not pending.
- **graded** — a score is present (primary and/or 2nd-grader).
- **pending** — gradable (deliverable exists) but not yet scored.

## Calibration discipline
Anchor 3 = adequate, 5 = excellent, 1 = poor. A pass that returns **uniform 5s across many cells** is a
red flag for an under-critical grader, not evidence of uniform excellence — flag it (`_CALIBRATION_FLAG_`)
rather than bank it. (See the no-think spot-grades, which carry exactly this flag.)

## What's been graded (as of 2026-05-31)
- **Primary (opus-4.7):** the 3 "full" microbench entries (doc-synthesis, market-research,
  adversarial-hallucination) + partial business-memo/PM dims, local AWQ only.
- **2nd-grader / inter-rater (opus-4.8, provisional):** doc-synthesis, market-research, adv-hallucination
  (reproducibility); Tier-A null fills (business-memo, PM); no-think spot-grades; big-model spot-grades.
- **Not graded (needs non-competitor grader):** the cloud entries (Opus/GPT-5.5), and a uniform rubric
  across cloud+local for a true ranking. See [`../MICROBENCH-INDEX.md`](../MICROBENCH-INDEX.md) and
  [`../QUALITATIVE-SPOT-GRADES.md`](../QUALITATIVE-SPOT-GRADES.md).
