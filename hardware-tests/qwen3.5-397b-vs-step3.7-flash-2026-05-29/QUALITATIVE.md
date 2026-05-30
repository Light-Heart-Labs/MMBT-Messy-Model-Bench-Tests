# Qwen3.5-397B-A17B vs Step-3.7-Flash — qualitative differences

**Status: N=10. Both 397B arms complete (no-think 82/120, think 72/120); Flash low/med/high complete; 27B/Coder via Q4/AWQ refs.**
Per-cell citations below may reference N=1 (`_v1`) artifacts where the behavior is identical across reps;
N=10 pass counts are in findings.md.
This doc is deliberately *not* a pass/fail scorecard. Pass/fail ties (397B no-think 8/12
vs Flash 7–8/12) hide the differences that matter — those live here. Every claim cites the
cell/file it came from so it's reproducible. See SCORECARD/findings for the quantitative table.

Models:
- **397B** = Qwen3.5-397B-A17B, UD-Q3_K_XL GGUF, llama.cpp b9014, pipeline (`-sm layer`), ctx 131072, no-think arm unless stated.
- **Flash** = Step-3.7-Flash-NVFP4, 201B MoE / ~11B active, vLLM, native CUTLASS FP4, reasoning levels low/med/high.
- Cross-engine + cross-quant: "best-as-each-ships," NOT a clean precision study.

## 1. Token / iteration economy — the sharpest split
Per-cell from `logs/<cell>/transcript.jsonl` (`iter`, `completion_tokens`, tool calls, `wall_s`):

| task | 397B no-think | Step-3.7 medium |
|---|---|---|
| p1_bugfix (both PASS) | 110 iters, 29.7k ctok, 463s | **333 iters, 107k ctok, 1222s** |
| p2_extract (both PASS) | 10 iters, 3.7k ctok | **3 iters, 2.0k ctok** |
| p2_ci | 42i / 6.4k | 28i / 13.2k |
| p3_doc | 20i / 12.6k | 11i / 9.9k |
| p3_business | 19i / 14.4k | 10i / 8.0k |
| p3_market | 75i / 17.6k | 96i / 28.4k |

**Read:** on the hard open-ended coding task both PASS, but Flash-medium burns ~3.6× the tokens
and 3× the iterations of 397B no-think. On the *trivial* grounded task (extraction) it inverts —
Flash is surgical (3 iters) where 397B plods (10). Flash's reasoning is a double-edged sword:
crisp when the task is well-bounded, flaily when it's open-ended. 397B no-think is steadier across
the difficulty range. Both hold ~1 tool call/turn (no thrashing).

## 2. Same conclusions, different packaging
`p3_business` (Borealis acquisition review, both PASS): both independently recommended **HOLD** and
cited the *same* core issues (burn-rate/runway math, thin customer validation, unsubstantiated
synergies, opaque valuation) — quality parity on the judgment. The form differs:
- **397B is scaffold-heavy:** 15 concerns in 3 severity tiers, two ADRs (incl. a concern-prioritization
  framework), a navigation README, per-deliverable "omissions" decision docs. (`logs/p3_business_397b-nothink_v1`, done_summary + workspace)
- **Flash is economical:** same substance as tighter flowing prose, fewer artifacts. (`logs/p3_business_step3p7-medium_v1`)

397B over-documents (useful if you want an audit trail, unprompted); Flash says it once and moves on.

## 3. Failure-mode texture (from grade.json sub-scores, not just verdict)
- **397B `p3_pm` FAIL = under-recall, not hallucination.** workstream_recall 6/6, milestone_recall 5/5,
  decision_recall 3/4, but **risk_recall 2/6** in a clipped 373-word output. It drops items when terse;
  it does not fabricate. Benign failure signature. (`logs/p3_pm_397b-nothink_v1/grade.json`)
- **397B `p3_writing` FAIL ≈ grader strictness, not bad output.** The legal_summary deliverable is
  accurate and audience-aware (correct incident window, tiered impact: 4 automation-failure / ~24
  enterprise / ~11,400 general accounts, defensible case-by-case credit recommendation) and it wrote
  ADRs documenting deliberate per-audience omissions. The binary grader rejected it anyway — real
  quality runs ahead of pass rate here. Ties to the known binary-grader-misses-quality caveat.
  (`logs/p3_writing_397b-nothink_v1` workspace)
- **397B `p1_testwrite` (think) FAIL = a *rule* violation hiding real competence.** After a grader-bug
  fix (see findings.md), the corrected metrics show think-mode wrote tests reaching **99% coverage / 153
  passing** — strong, capable test-writing. It FAILs only because it edited `logalyzer/` production code,
  violating the task's "only /tests/ may differ" rule (`logalyzer_unchanged: False`). The prior grader bug
  reported `cov=0` and made this look like a flat incapacity ("coverage never improves"). Lesson: a broken
  metric doesn't just mis-score — it **invents the wrong story about why**. The pass/fail bit (FAIL) was
  right by accident; everything it implied about the model was wrong. (`logs/p1_testwrite_397b-think_v1/grade.json`)

## 4. Does thinking help 397B? Net −10 at N=10 — it *redistributes*, and on net hurts
**No-think 82/120 vs think 72/120.** The signal sharpened with N: at N=1 the loss looked like a single
verbosity flip (`p3_doc`); N=3 hinted at redistribution (−1); **N=10 makes it decisive** — thinking moves
three cells, hard, in both directions while leaving the other nine identical:

| cell | no-think (N=10) | think (N=10) | Δ | what's happening |
|---|:--:|:--:|:--:|---|
| **p3_market** | 8/10 | **10/10** | +2 | thinking *stabilizes* the wobbliest cell — clears the no-think stall, zero runaways |
| **p3_pm** | 5/10 | **0/10** | −5 | thinking *destroys* project-mgmt synthesis (over-deliberation) |
| **p3_doc** | 9/10 | **2/10** | −7 | the verbosity story: thinking inflates length, trips the 700-word limit |

The verbosity mechanism is well-captured: think `p3_doc` hits the same fact coverage as no-think but
overruns the 700-word limit (e.g. 721 vs 692 words at N=1) — equal substance, failed on form. **Lesson:
reasoning changes *where* 397B succeeds, not *how often* — and here the trade is net-negative.** "Turn
thinking on" is a per-task decision; for doc-synthesis and project-mgmt it's actively harmful, for market
research it's a clear win.

**Reasoning shape:** 397B thinks in short targeted bursts (`p1_bugfix` think: 16 of 126 turns carry a
substantial think block, median ~73 reasoning tokens/turn), not long monologues — but uses more turns
than no-think on the same task (126 vs 110).

**No *runaways*, but no-think *stalls* on market research.** Zero max_tokens/length failures across all
240 N=10 cells — contrast Flash, which **ran away on `p3_market` at low effort**, and 27B-Q8 which ran
away 23/36 times. 397B's failure mode is the opposite of runaway: its only non-clean exits are *stalls*
(stuck-loop / `model_stopped`), concentrated in no-think `p3_market`/`p3_pm`. Thinking specifically clears
the no-think market stall (think `p3_market` 10/10). So the reliability edge over Flash is real
(no runaways), but it's "stalls quietly," not "always finishes."

## 5. Integration cost (a "messy model" finding in itself)
- Flash (vLLM) ran the harness out of the box once launched.
- 397B (llama.cpp) needed two fixes: **`--reasoning-format none`** (default extracts CoT into
  `reasoning_content`, leaving `content` empty → the agent loop reads a thinking turn as "done" and dies
  at iter ~3; the no-think smoke could not catch this) and a **sandbox-cleanup workaround** (non-sudo
  `rm` fails on root-owned workspace leftovers; sandbox containers not force-removed on abnormal exit →
  re-run name collisions). Both are harness/engine-integration bugs, not model quality — but they're
  exactly the "messy" friction MMBT exists to document. PR should fix both in the harness.

## Net take (N=10, both arms)
397B no-think is the steady, over-documenting, high-prose-quality one whose misses are omissions; Flash
is the fast, terse, reasoning-driven one — brilliant when bounded, flaily when not. They agree on
substance more than the scorecard's "tie" suggests. Flash is the cheaper/faster way to the same band
(~99 vs ~71 tok/s, one engine vs both GPUs). 397B's edge is reliability — no max_tokens runaways (its
worst case is a quiet *stall* on no-think market research, which thinking clears to 10/10) — not raw
accuracy. Thinking lowers the aggregate (net −10 at N=10); it *redistributes* (market up, pm/doc down), so
"turn thinking on" is a per-task call, not a default. Reach for 397B when runaway resistance and
market-research reliability matter; otherwise Flash wins on speed and cost.
