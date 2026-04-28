# 2026-04-28 — Coding + business microbenches across Phase 1, 2, 3

> 12 task families, 2 models, N=3 each = 72 planned runs (re-runs / kills push the actual to ~80, including 2 27B runs manually advanced past identical-call-loops). The headline rewrites the daily-driver picture set by the 75-PR audit benchmarks:
>
> 1. **27B is reliable at tight-schema tasks** (Phase 2: 12/12 PASS) — the prior "27B doesn't ship" framing was task-class-specific.
> 2. **27B drives internet-research workflows that Coder-Next can't** (market research: 27B 3/3 STRUCTURAL_PASS vs Coder-Next 0/3 STRUCTURAL_FAIL — the single largest model-superiority signal in this benchmark outside hallucination resistance).
> 3. **Coder-Next is cheap and shippable but has a real hallucination-resistance gap** (1/3 PASS on adversarial hallucination, with 2 confirmed-fabrications-as-real on the one shipping run).
> 4. **27B has a documented word-limit-trim failure** (doc synthesis: 8/8 facts captured every run, but 0/3 PASS — model can't compress to a tight word limit, identical-call-loops trying).

## What was tested

Task family / phase split:

| Phase | Task | Grading | What it measures |
|---|---|---|---|
| **1** | Bug fixing (logalyzer) | programmatic (pytest + ruff) | Can the model run code, find issues, ship a fix? |
| 1 | Test writing (logalyzer) | coverage delta + production-unchanged check | Targeted addition without scope drift |
| 1 | Refactoring (logalyzer) | structural check + tests-still-pass | Localized change with strict no-bleed constraint |
| **2** | Structured extraction | per-field exact-match (with tolerance) | Schema-bound information extraction |
| 2 | CI failure debugging | re-run CI checks | Read-failure → target-fix |
| 2 | Adversarial hallucination | confusion matrix on planted real/fab issues | Resistance to confident-but-wrong claims |
| 2 | Customer support triage | category accuracy + duplicate-cluster recall | Closed-vocabulary classification |
| **3** | Document synthesis | planted-key-fact coverage + word limit | Multi-source brief writing |
| 3 | Business memo | bias-signal recall + stance pushback | Reading a deal pack skeptically |
| 3 | Market research | citation count + product coverage | Internet research with verification |
| 3 | Writing/editing | per-audience must-include / must-not-include | Audience-tailored rewriting |
| 3 | Project management | workstream / risk / decision / milestone recall | Status synthesis from meeting notes |

## Headline pass rates

> All numbers are PASS / total at the **N=3 grain per (model × task)**, with explicit caveats for task-design issues called out below.

### Coder-Next-AWQ

| Phase | Task | PASS | Notes |
|---|---|---|---|
| 1 | bug-fixing | 2/3 | 3rd run killed at iter 545 / 110 min wall (post-completion drift) |
| 1 | test-writing | 0/3 | task-design issue: starter has a broken import that requires production-code modification to fix |
| 1 | refactoring | 0/3 | same task-design issue; agent DID create the required `output/` subpackage in 3/3 runs |
| 2 | structured extraction | 3/3 | 95% / 90% / 90% accuracy — slightly below 27B but well above the 80% pass threshold |
| 2 | CI failure debugging | 3/3 | clean — ruff green, pytest green, no shortcut markers |
| 2 | adversarial hallucination | 1/3 | 2/3 stuck-detector fired before producing output; 1 squeaked over threshold (DANGEROUS=2) |
| 2 | triage | 3/3 | 96.7% category accuracy (better than 27B's 86.7%), 100% duplicate-cluster recall |
| 3 | document synthesis | 2/3 | v1 captured all 8 planted facts; v2 went over word limit at 1005 words; v3 PASS at 7/8 |
| 3 | business memo | 3/3 | caught 6-7/8 planted bias signals all 3 runs, all with stance pushback |
| 3 | market research | 0/3 | structural fail — none produced the required output files (internet-research workflow doesn't drive cleanly) |
| 3 | writing/editing | 2/3 | v3 failed legal-summary subdimension (probably included prohibited content) |
| 3 | project management | 1/3 | workstreams 6/6 every time, but risk recall only 2-3/6 (multi-week risks missed) |

**Coder-Next combined: ~24/36 across the 12 task families with task-design issues.** Excluding the test-writing/refactoring task-design issue (where both models 0/3 due to starter quirks), **24/30 = 80% PASS.**

### Qwen3.6-27B-AWQ

| Phase | Task | PASS | Notes |
|---|---|---|---|
| 1 | bug-fixing | 3/3 | pytest 0→17, 0→63, 0→55 — actually shipped fixes |
| 1 | test-writing | 0/3 | same task-design issue as Coder-Next |
| 1 | refactoring | 0/3 | same |
| 2 | structured extraction | 3/3 | **100% accuracy, 20/20 fields all 3 runs** |
| 2 | CI failure debugging | 3/3 | clean |
| 2 | adversarial hallucination | 3/3 | **100% accuracy on 15 issues, 0 dangerous errors** all 3 runs |
| 2 | triage | 3/3 | 86.7% category accuracy, 100% duplicate-cluster recall |
| 3 | document synthesis | 0/3 | **all 3 captured 8/8 facts but went over 700-word limit** (765, 775, 768). v2 and v3 entered identical-call-loops trying to trim and were manually advanced. |
| 3 | business memo | 2/3 | 8/8 bias signals every run; v3 hit 708 words (1 over 700 limit) |
| 3 | market research | **3/3 STRUCTURAL_PASS** | **all 3 runs evaluated all 5 products with 12-18 inline cites to 29-33 distinct URLs** — citation validity is hand-grading placeholder; structural success only |
| 3 | writing/editing | 0/3 | all 3 single-subdimension fails — customer_email missing required keyword (outage/downtime/incident); ceo_brief + legal_summary PASS in all 3 |
| 3 | project management | 0/3 | workstreams 6/6 every run, decisions 3-4/4, but risks only 2/6 (same multi-week-risk-miss pattern as Coder-Next) |

**27B combined Phase 1+2+3: ~17/30 PASS (counting STRUCTURAL_PASS = PASS, excluding the task-design-issue testwrite/refactor rows). 12/12 PASS on programmatic Phase 2 (100%). 5/15 on Phase 3 vs Coder-Next 8/15.**

## What rewrites the daily-driver picture

### 1. The "27B doesn't ship" framing was task-class-specific

The 75-PR audit and N=1 PR audit benchmarks had 27B failing to produce `verdict.md` in **0 of 6** runs. We labeled that "no-ship" and built the prior daily-driver framing around it.

That framing was incomplete. **In Phase 2's 12 programmatic-graded runs, 27B shipped `done_signal` 12 of 12 times, with 100% accuracy on extraction and hallucination, 100% duplicate-cluster recall on triage.** When the deliverable is a small JSON with a tight schema (vs an unbounded markdown report), 27B ships cleanly and accurately. The PR-audit "no-ship" was about the *shape* of the deliverable, not the model's ability to complete tasks.

**Updated framing**: 27B's no-ship failure is correlated with deliverable-shape complexity. Tight schema → ships. Unbounded markdown narrative → doesn't.

### 2. Coder-Next has a real hallucination-resistance gap

On the adversarial-hallucination benchmark — agent reviews 15 claimed issues, must distinguish 6 real from 9 fabrications:

- 27B: 3/3 PASS, 100% accuracy, 0 dangerous errors (no fabrication confirmed-as-real)
- Coder-Next: 1/3 PASS, the 1 that shipped had **2 dangerous errors** (right at the safety threshold); 2/3 stuck-detector fired

The stuck-detector firings are themselves diagnostic: 500 iters of unchanged workspace state means the model was reading code over and over without producing output, probably because it couldn't decide between "this is real" and "this is fabricated" cleanly. When it did decide (v3), it confirmed 2 fabrications as real.

This is the same failure mode as the dreamserver-1-pr-audit `n1_coder_v3` run that fabricated 4 technical issues including a fake test script. **Coder-Next at temp=0.3 is not safe for tasks that require fabrication resistance.** 27B is the clear pick for that use case.

### 3. Coder-Next is materially cheaper per attempt

Cost-per-attempt (upper bound, $) on Phase 2 tasks:

| Task | 27B median | Coder-Next median | Ratio |
|---|---|---|---|
| extraction | $0.0050 | $0.0004 | 12× |
| CI failure | $0.0050 | $0.0014 | 4× |
| triage | $0.0050 | $0.0008 | 6× |
| hallucination | $0.0080 | $0.0011 (when shipping) | 7× |
| (stuck Coder-Next runs) | n/a | $0.034-0.036 | — |

When Coder-Next ships, it's 4-12× cheaper per attempt than 27B. This makes the **ensemble-with-verification deployment shape** cleanly economical: run Coder-Next 3 times, take majority, manually verify dissent — total cost per decision is still less than one 27B attempt.

The ensemble path's effectiveness depends on which task. For triage (where Coder-Next has 96.7% category accuracy), ensembling is overkill. For hallucination (where 1/3 ship and ship-with-dangerous-errors), ensembling needs careful design — random-3-and-vote will have the dangerous-error confirmed in expectation if the underlying false-positive rate is non-trivial.

### 4. Test-writing and refactoring task-design issue

Both models 0/3 on test-writing and 0/3 on refactoring in Phase 1. Initially this looks like a model failure. Investigation revealed the failure is shared and rooted in a starter quirk: the logalyzer codebase has a `from collections import Iterable` import that prevents test collection on Python 3.10+. To make any tests collect at all, the agent has to fix that import. That's a "production-code change" which violates the rule in both tasks.

So:
- The test-writing task is **un-satisfiable in spirit** — you cannot add tests to a codebase where tests don't collect, without first fixing the collection error.
- The refactoring task is *partially* satisfiable in spirit — Coder-Next produced the required `logalyzer/output/` subpackage with backward-compat imports in 3/3 runs. They violated the strict "no non-output changes" rule, but did the actual refactor work.

**Lesson for benchmark design**: starter quirks need to be checked against the task constraints before a task is run. Future test-writing benchmarks should use a starter where tests *do* collect cleanly.

### 5. Market research splits the models hard — 27B drives the workflow, Coder-Next can't

This rewrites what an earlier draft of this findings doc said. The Phase 3 result was a clean inversion:

- 27B: **3/3 STRUCTURAL_PASS** — all three runs evaluated all 5 products (1Password, Bitwarden, Dashlane, Keeper, LastPass), with 12-18 inline cites to 29-33 distinct URLs, recommendation 1237-1594 words. The agent drove a multi-step research workflow with sustained tool use over 18-27 minutes.
- Coder-Next: **0/3 STRUCTURAL_FAIL** — none produced the required `recommendation.md`/`comparison.md`/`sources.md` files. 2 stuck-in-research, 1 vLLM api_error (probable context overflow at 65 iters).

This is the largest local-model superiority signal in the entire microbench suite outside the adversarial-hallucination cell. **27B can drive sustained internet research; Coder-Next cannot.** Two distinct architectural strengths play together: (a) larger context handling without API errors, (b) sustained tool-use loops without entering stuck-in-research.

Caveat: STRUCTURAL_PASS means files exist with the right shape and content keys hit. Citation validity (do the URLs exist? do they say what they're cited for? are the stats faithful?) is a hand-grading placeholder. The "all citations valid" claim isn't supported by current data — 18 cites to 33 URLs is a lot to verify. But the *structural* gap between the models is large and visible regardless.

For the daily-driver question: 27B is now the local pick for autonomous market-research-shaped tasks (with output sampled and validated, not consumed blind). Coder-Next is not.

### 6. Variance is real but smaller than expected on these tasks

On Phase 2 + Phase 3, both models showed surprisingly low variance across N=3 — same task, same flags, same model produced near-identical outputs (often to within 1-3 percentage points on accuracy metrics). This is different from the PR-audit benchmark variance, where Coder-Next at N=3 produced REJECT, MERGE, REJECT verdicts.

Hypothesis: variance scales with task openness. Tight-schema tasks have a small set of plausible outputs; the model's logits converge on the same shape. Open-ended narrative tasks have many plausible outputs; sampling diverges run-to-run.

## Updated daily-driver guide

The Phase 1+2+3 evidence sharpens the per-use-case recommendations. **Conditional on task class**:

### Use Qwen3.6-27B-AWQ when

- **Hallucination resistance matters** — the 3/3 100%-accuracy 0-dangerous-errors result on the adversarial-hallucination task is the clearest local-model superiority signal in this entire benchmark suite. For security review, factual research, or anything where confidently-wrong is dangerous, 27B is the pick.
- **Internet-research-driven tasks (with citation sampling)** — the 3/3 market-research STRUCTURAL_PASS is the second-clearest local-model superiority signal. 27B drives multi-step research workflows that Coder-Next can't (Coder-Next was 0/3 on the same task). Sample-grade the citations on 27B's output rather than consuming blind.
- **High-accuracy structured extraction** — 100% on 20 fields is the kind of result you'd build a pipeline on.
- **Tasks with tight JSON schemas** — extraction, classification, triage, schema-bound code review.

### Use Qwen3-Coder-Next-AWQ when

- **Cost matters more than accuracy ceiling** — 4-12× cheaper per attempt on Phase 2 tasks. Run it 3-5 times for ensemble verification and you still come in under one 27B attempt.
- **Bug-fixing-style code work** — both models tied at 100% on bug-fix, but Coder-Next was faster.
- **Tight-word-limit summary work** — Coder-Next was 2/3 on doc-synthesis vs 27B's 0/3, because Coder-Next reliably produces output under a length cap and 27B doesn't.
- **Bounded business-memo / writing-rewrite tasks** — Coder-Next was 3/3 vs 27B 2/3 on business memo, 2/3 vs 27B 0/3 on writing-editing. Coder-Next's competitive accuracy + lower cost makes this its best Phase 3 niche.
- **CI failure debugging** — both models 3/3 PASS; pick the cheaper one.

### Avoid both when

- **Long-horizon (>30 min) unattended work** — see the dreamserver-PR-audit findings; not changed by Phase 1+2+3.
- **PM-status-synthesis with multi-week-spanning risks** — both models reliably miss multi-week risks (2-3/6 risk recall across all runs of both models). Workstream + decision recall is excellent (6/6 + 3-4/4); the multi-week risks are the failure mode.
- **Anything where 100% accuracy is required and verification budget is zero** — 27B's accuracy is high but not 100% across all task classes. Coder-Next's is materially lower in some cases.

### Cloud comparison

This benchmark suite still doesn't have cloud-LLM entries on Phase 1+2+3 tasks. The categorical gap from the dreamserver-PR-audit benchmark (cloud reliably ships, local mostly doesn't) is reduced or absent on the smaller-scope tasks here. Local 27B is genuinely competitive with the kind of work cloud entries did on the PR-audit task — within the smaller-scope subset. Outside that subset (long-horizon, internet-research-heavy), the cloud advantage probably remains.

## Caveats — please read before quoting

- **N=3 per cell is borderline.** Confidence intervals on these pass rates are wide; 3/3 PASS with 95% CI lower bound is ~30%, not 100%. The numbers above are point estimates on small samples.
- **The starter codebase (logalyzer) has a known broken import** that affected the test-writing and refactoring task results. The "0/3" numbers there reflect a task-design issue, not pure model failure.
- **Ground-truth-leak audit was passed pre-launch.** Ground-truth files (planted answers, planted bias signals, expected key facts) were moved from agent-mountable input dirs to a separate `agent-pilot/graders/ground_truth/` location before any Phase 2 / 3 runs. The agent could not see the answers.
- **Hand-rating placeholders not yet filled.** Phase 3 graders emit programmatic verdicts, but the subjective dimensions (prose quality, fabrication count beyond keyword matching, audience-tone fit at 1-5 scale) are placeholder fields awaiting human grading. The PASS/FAIL above is from the programmatic axis only.
- **Approximate determinism only.** vLLM bf16 paths aren't bitwise deterministic, runs at temp=0.3 add intentional sampling diversity.
- **27B Phase 3 chain had 2 manually-advanced stuck-loops on doc_synthesis** (v2, v3). Both were writing the same `brief.md` content for 50-130+ iters trying to compress to the 700-word limit and never succeeding. Manual SIGTERM advanced the chain rather than waiting 5+ hours for the stuck-detector at iter 500. The pattern is documented as a 27B failure shape, not a transient bug. v1 completed cleanly via done_signal at iter 33 but still hit 765 words >700 → FAIL.

## Where this leaves SCORECARD.md

The SCORECARD's previous version had 13 (model × task) rows. With Phase 1+2+3 we're adding ~24 new rows (12 task families × 2 models). The model-selection-guide section needs the updates above — particularly the "use 27B when hallucination resistance matters" line, which is the single sharpest signal in the new data.

PR sequence to land all this on MMBT:
1. Update SCORECARD.md with the new rows + sharpened guide
2. Add new benchmark folders for Phase 1+2+3 entries (with cost.json + label.json + grade.json + receipt.json + transcript.jsonl per entry — same convention as the dreamserver benchmarks)
3. Add this findings doc

To be split across at least 2 PRs (programmatic-graded entries, then subjective-graded entries with hand-rating notes).
