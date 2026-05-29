# Qwen3.5-397B-A17B vs Step-3.7-Flash — qualitative differences

**Status: N=1 / provisional. Both 397B arms complete (no-think 8/12, think 7/12); Flash low/med/high complete.**
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

## 4. Does thinking help 397B? Net −1 — and N=3 shows it *redistributes*, not "does nothing"
**No-think 23/36 vs think 22/36** (N=1 was 8/12 vs 7/12 — net −1 both ways). At **N=1** the loss looked
like a single verbosity flip (`p3_doc`), and it was tempting to call thinking "inert everywhere else."
**N=3 refutes that** — thinking moves three cells, in *both* directions:

| cell | no-think (N=3) | think (N=3) | Δ | what's happening |
|---|:--:|:--:|:--:|---|
| **p3_market** | 1/3 | **3/3** | +2 | thinking *stabilizes* the wobbliest cell — coin-flip → lock, zero runaways |
| **p3_pm** | 2/3 | **0/3** | −2 | thinking *hurts* project-mgmt synthesis (over-deliberation → worse) |
| **p3_doc** | 2/3 | 1/3 | −1 | the verbosity story: thinking inflates length, trips the 700-word limit |

The N=1 `p3_doc` flip was real but *not the whole story* — one draw of a three-way swing. The verbosity
mechanism is well-captured: at N=1, think `p3_doc` hit **all 8/8 facts** (`fact_coverage 1.0`, same as
no-think) but wrote 721 words vs the 700 limit (no-think: 692) — equal substance, failed on form
(`logs/p3_doc_397b-{nothink,think}_v1/grade.json`). The new lesson from N=3: **reasoning changes *where*
397B succeeds, not *how often*** — it buys market-research reliability at the cost of pm/doc, netting to
−1. A single-N read would have missed both the gain and the symmetry.

**Reasoning shape:** 397B thinks in short targeted bursts (`p1_bugfix` think: 16 of 126 turns carry a
substantial think block, median ~73 reasoning tokens/turn), not long monologues — but uses more turns
than no-think on the same task (126 vs 110).

**No runaways, either mode.** All 12 think cells finished `done_signal` (no max_tokens/length failures) —
including `p3_market` (STRUCTURAL_PASS, 56 iters). Contrast Flash, which **ran away on `p3_market` at low
effort** (hit max_tokens). 397B is runaway-resistant in both modes; Flash's runaway risk is concentrated
at low reasoning effort. This is a real reliability edge for 397B.

## 5. Integration cost (a "messy model" finding in itself)
- Flash (vLLM) ran the harness out of the box once launched.
- 397B (llama.cpp) needed two fixes: **`--reasoning-format none`** (default extracts CoT into
  `reasoning_content`, leaving `content` empty → the agent loop reads a thinking turn as "done" and dies
  at iter ~3; the no-think smoke could not catch this) and a **sandbox-cleanup workaround** (non-sudo
  `rm` fails on root-owned workspace leftovers; sandbox containers not force-removed on abnormal exit →
  re-run name collisions). Both are harness/engine-integration bugs, not model quality — but they're
  exactly the "messy" friction MMBT exists to document. PR should fix both in the harness.

## Net take (provisional, no-think only)
397B no-think is the steady, over-documenting, high-prose-quality one whose misses are omissions; Flash
is the fast, terse, reasoning-driven one — brilliant when bounded, flaily when not. They agree on
substance more than the scorecard's "tie" suggests. Flash is the cheaper/faster way to the same band
(~99 vs ~71 tok/s, one engine vs both GPUs); 397B's case is narrow (long-form synthesis reliability,
one stable setting, no effort-tuning). The 397B-think arm is the apples-to-apples test against Flash's
reasoning modes — pending.
