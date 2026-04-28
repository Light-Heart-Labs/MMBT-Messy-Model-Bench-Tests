# Scorecard

> Single-table comparison across the published entries. The detail lives in entry READMEs and findings docs; this is the synthesis.
>
> **Read [`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md) before quoting any cell.** Several columns are hand-graded against ground truth where it exists, "not graded" where it doesn't. Confidence levels are noted per column.

## What the columns mean

- **Runs published**: how many of the model's attempts on this task are represented in MMBT, vs how many were attempted total (in the source bench repo). Cherry-picked-best-of-N is the publishing default for entries where any attempt shipped; the other attempts are described in entry READMEs.
- **Spec compliance**: did the run produce all required artifacts the task spec asked for? *Strong evidence* — file existence is checkable.
- **Factual accuracy**: for tasks with verifiable ground truth, does the model's verdict match? *Strong evidence on dreamserver-1-pr-audit* (PR #1057 has a known-correct MERGE per the canonical hand-written review and the Opus-4.7 audit). *Not graded* on dreamserver-75-pr-audit (would need per-PR ground truth across all 75) or on wallstreet (BUY/HOLD/SELL is opinion, not verifiable as right/wrong without market hindsight).
- **Fabricated claims**: count of hand-graded false-but-confident technical claims in the verdict / review (e.g. citing line numbers for issues that aren't in the diff, asserting behavior the code doesn't have). *Strong evidence on dreamserver-1-pr-audit*. *Not graded* elsewhere yet — would need a per-claim rubric pass over hundreds of claims.
- **Tests actually run**: did the agent invoke the upstream test suite during the run? *Strong evidence* — visible in the transcript.
- **Wall**: median (or single-run) wall time. Hardware-specific (Tower2 — see KNOWN-LIMITATIONS).
- **Cost (upper)**: upper-bound USD estimate from `cost.json`. Assumes the GPU drew at its `power.limit` for the entire run; real draw is lower. *Suggestive only* — for ranking, not for absolute economics.
- **Failure mode**: the primary `label.json` taxonomy entry (`tooling/FAILURE-TAXONOMY.md`).

---

## dreamserver-75-pr-audit

> Audit 75 open PRs in a live repository and produce a traceable maintainer triage repo.

| Model | Runs | Spec | Factual accuracy | Fabricated | Tests | Wall | Cost | Failure mode |
|---|---|---|---|---|---|---|---|---|
| **Opus-4.7** (cloud) | 1/1 | ✓ full | not graded (would need per-PR ground truth across all 75) | not graded | not visible from artifacts | ~5 hr | n/a | success-shipped |
| **GPT-5.5** (cloud) | 1/1 | ✓ full + `verify_coverage.py` self-check passes | not graded | not graded | not visible from artifacts | not recorded | n/a | success-shipped |
| **Qwen3.6-27B-AWQ** (local) | 1/3 published | △ 75/75 verdict.md *files* but only 3 are real reviews; 72 are template stubs | partial (3 reviewed PRs match ground truth; 72 stubs unverified) | 0 in the 3 deep reviews | **0** | 24 min | $0.031 | scaffold-and-stop |
| **Qwen3-Coder-Next-AWQ** (local) | 0/5 | ✗ no deliverable across 5 attempts | n/a | n/a | n/a | 1-42 min | $0.001-$0.054 | identical-call-loop, cyclic-name-slop, stuck-in-research |

## dreamserver-1-pr-audit (PR #1057, known-correct verdict: MERGE)

> Same task spec scaled to a single PR. Ground truth on PR #1057 established three independent ways: canonical hand-written review, the actual public diff, Opus-4.7's audit. All three agree: MERGE. The catalog-handling architectural distinction (`_handle_model_list` vs `_handle_model_download`) is the trap that separates surface-pattern matchers from architectural readers.

| Model | Runs | Spec | Factual accuracy | Fabricated | Tests | Wall | Cost | Failure mode |
|---|---|---|---|---|---|---|---|---|
| **Qwen3-Coder-Next-AWQ** | 1/3 published (cherry-picked correct) | ✓ 13/13 files, tag, done() | **2/3 wrong** across the three runs (this entry's run is the 1 correct; v1 and v3 said REJECT incorrectly) | 1 in v1, **4 in v3** including a fabricated `test_stderr_truncation.py` | repro script, no execution | 3 min | $0.004 | success-shipped (cherry-picked) |
| **Qwen3.6-27B-AWQ** | 1/3 published | ✗ 7/13 files; **no verdict.md, no tag, no done()** in any of 3 runs | 3/3 implicit-MERGE-correct (in `review.md`'s Summary of Findings table; never in a `verdict.md`) | 0 | **pytest invoked, 38 tests on both branches** | 7 min | $0.009 | partial-no-spec-output |
| **Qwen3.6-35B-A3B-AWQ** | 1/1 | ✗ 0/13 — zero artifacts | n/a (nothing produced) | n/a | pytest run but no artifacts written | 1.7 min | $0.002 | floor-failure |

## wallstreet-intern-test

> Build a complete investment memo on any publicly traded US company with $1B-$10B market cap. Every number traceable from raw source → model → memo. Recommendations (BUY/HOLD/SELL) are opinion, **not graded as right/wrong** — the verifiable axes are spec compliance, source traceability, and fabrication count.

| Model | Company | Rec | Runs | Spec | Factual accuracy | Fabricated | Wall | Cost | Failure mode |
|---|---|---|---|---|---|---|---|---|---|
| **Opus-4.7** (cloud) | Vita Coco (`COCO`) | HOLD ($46 vs $52 spot) | 1/1 | ✓ full memo + machine-readable verification | not graded (opinion) | not graded | not recorded | n/a | success-shipped |
| **GPT-5.5** (cloud) | YETI Holdings (`YETI`) | HOLD ($41) | 1/1 | ✓ full memo + verification + board-deck follow-on | not graded (opinion) | not graded | not recorded | n/a | success-shipped |
| **Qwen3.6-27B-AWQ** (local) | GitLab (`GTLB`) | BUY | 1/3 published | ✓ full memo + 17 KB XLSX | not graded (opinion) | not graded | 27 min | $0.032 | success-shipped (cherry-picked) |
| **Qwen3-Coder-Next-AWQ** (local) | DocuSign (`DOCU`) | BUY | 1/3 published | ✓ full memo + 10.6 KB XLSX | not graded (opinion). **Caveat: this model's PR-audit verdicts were 2/3 wrong with fabricated evidence; same risk likely extends to BUY calls** | not graded | 11 min | $0.013 | success-shipped (cherry-picked) |
| **Qwen3.6-35B-A3B-AWQ** (local) | — | — | 0/3 | ✗ no usable deliverable | n/a | n/a | 0.2-7 min | $0.0002-$0.0085 | floor-failure / api-error / stuck-in-research |

---

## microbench-2026-04-28 (12 task families × 2 models × N=3)

> Smaller-scope task families than the dreamserver/wallstreet benchmarks above — each task is a 5-30 minute deliverable rather than a multi-hour audit. Phase 1 = coding (programmatic graders). Phase 2 = structured business tasks (programmatic graders). Phase 3 = unbounded business/writing tasks (mix of programmatic + hand-grading placeholders). N=3 per cell. Cherry-picked-best-of-N is **not** the publishing default here — the table reports N=3 PASS rates so variance is visible. See [`benchmarks/microbench-2026-04-28/findings.md`](benchmarks/microbench-2026-04-28/findings.md) for cross-cutting analysis. Entries published only for the most signal-rich task families to avoid bloating the repo with 60+ tiny folders; full results table reproduced below for completeness.
>
> **Two task-design issues called out separately**: `p1_testwrite` and `p1_refactor` use a shared starter (`logalyzer/`) with a known broken import (`from collections import Iterable` — Python 3.10+ removed this). Both models 0/3 PASS on these — but the failure is fixing-the-starter-vs-task-scope tension, not pure model failure. See findings doc § "Test-writing and refactoring task-design issue".

| Phase | Task | 27B PASS | Coder-Next PASS | 27B median wall | Coder median wall | 27B median cost | Coder median cost | Notable |
|---|---|---|---|---|---|---|---|---|
| **1** | bug-fixing (logalyzer) | **3/3** | 2/3 | 18.0 min | 11.5 min | $0.023 | $0.015 | both ship; coder-v3 killed at iter 540 (post-completion drift) |
| 1 | test-writing (logalyzer) | 0/3 † | 0/3 † | 9.6 min | 14.0 min | $0.012 | $0.018 | task-design issue (broken import) — see caveat |
| 1 | refactoring (logalyzer) | 0/3 † | 0/3 † | 5.4 min | 5.4 min | $0.007 | $0.007 | task-design issue — see caveat |
| **2** | structured extraction | **3/3** | **3/3** | 1.2 min | 0.3 min | $0.0015 | $0.0004 | 27B 100% on 20 fields; coder ~92% |
| 2 | CI failure debugging | **3/3** | **3/3** | 2.1 min | 1.2 min | $0.003 | $0.0015 | both clean; coder cheaper |
| 2 | adversarial hallucination | **3/3** | 1/3 | 3.4 min | 25.9 min | $0.004 | $0.034 | 27B 100% / 0 dangerous; coder 2/3 stuck-detector fired, ship-with-2-dangerous-errors |
| 2 | customer support triage | **3/3** | **3/3** | 3.3 min | 1.0 min | $0.004 | $0.0013 | coder 96.7% category, 27B 86.7% (both 100% dup-cluster recall) |
| **3** | document synthesis | 0/3 †† | 2/3 | 32.7 min ‡ | 0.6 min | $0.043 ‡ | $0.0008 | 27B 8/8 facts every run but couldn't trim to 700 words (765, 775, 768); 2 of 3 stuck in identical-call-loop trying to trim. coder hit limit 2/3. |
| 3 | business memo | 2/3 | **3/3** | 2.8 min | 0.5 min | $0.0037 | $0.0007 | both 8/8 bias signals every run; 27B v3 hit 708 words (1 over) |
| 3 | market research | **3/3 ★** | 0/3 | 18.9 min | 19.1 min | $0.025 | $0.025 | **27B drives the internet-research workflow Coder-Next doesn't.** All 3 27B runs evaluated all 5 products with 12-18 inline cites to 29-33 distinct URLs. Coder-Next 0/3 STRUCTURAL_FAIL across all 3 runs. |
| 3 | writing/editing (3-audience rewrite) | 0/3 | 2/3 | 2.8 min | 0.4 min | $0.0036 | $0.0005 | 27B 0/3 all single-subdimension fails (customer_email missing required keyword); ceo_brief + legal_summary PASS in all 3 |
| 3 | project management synthesis | 0/3 | 1/3 | 1.3 min | 0.3 min | $0.0017 | $0.0003 | both: workstreams 6/6 every run, but only 2-3/6 risks recalled (multi-week risks missed) |

> † `p1_testwrite` / `p1_refactor` failures are correlated with starter-codebase task-design issue; see microbench findings doc § "Test-writing and refactoring task-design issue" before drawing model-quality conclusions from these rows.
>
> †† All 3 27B doc-synthesis runs captured all 8 planted facts but couldn't trim to the 700-word limit. 2 of 3 (v2, v3) hit identical-call-loop on the same brief.md content for 50-130+ iters and were manually advanced to keep the chain moving. Pattern is a documented 27B failure shape, not a transient bug.
>
> ‡ 27B doc-synthesis median wall is dominated by the wall-killed v2/v3 runs (32.7 min, $0.043). The cleanly-completed v1 was 8 min / $0.011.
>
> ★ Inversion vs the prior expectation in the findings doc: 27B *can* drive sustained internet-research workflows that Coder-Next doesn't. **Citation-validity pass (18 of 33 URLs from `p3_market_27b_v1` validated on 2026-04-28): 9 strong-valid (factual claim exactly matches live page), 3 partial-valid (claim mostly right with minor specificity issues), 2 confirmed-wrong URLs (404), 4 inaccessible to the validator. Of 14 testable URLs, 12 (86%) are mostly-valid and 9 (64%) are strict-valid. Measured `citations_valid_pct = 75` (was 90 estimate). `fabricated_stats_count = 0` — every checkable factual claim (prices, certifications, products) matched live data.** Critical observation: the error mode is URL drift (wrong or dead URLs cited), not fabricated facts — a meaningfully different failure shape than the dreamserver-1-pr-audit Coder-Next variance that fabricated technical evidence with confident citations.

**Headline reads from this table:**

- **Aggregate is tied at 20/36 vs 20/36 (55.6% / 55.6%).** Across the 12 task families × N=3, both models PASS exactly 20 cells. They tie on overall pass rate but win on different task classes — 27B wins adversarial-hallucination, market-research, bug-fixing; Coder-Next wins doc-synthesis, business-memo, writing-editing, project-management; both tie on extraction, CI, triage. The right framing is **complementary, not interchangeable, not strictly ranked**: pick by task class, default to Coder-Next when class is uncertain or cost matters.
- **Coder-Next is 2-5× faster and 4-12× cheaper per attempt** on every cell where both ship. This is the most decisive Coder-Next-favoring signal in the data. When task-class accuracy is roughly matched (the 5 ties + the 4 Coder-Next-wins task families = 9 of 12 task families), Coder-Next is the operational pick.
- **27B is reliable on tight-schema tasks.** Phase 2's 12 programmatic-graded runs: 12/12 PASS. The "27B doesn't ship" framing from the dreamserver-PR-audit benchmark was task-class-specific — when the deliverable is a constrained-shape JSON or markdown-with-clear-keys, 27B ships cleanly.
- **27B has a documented word-limit-trim failure mode.** Doc-synthesis: 8/8 planted facts captured every single run, but 0/3 PASS because the model cannot reliably compress to a tight word limit. 2 of 3 runs entered identical-call-loops trying. Coder-Next handled this better (2/3 PASS).
- **Big inversion on market research.** 27B was 3/3 STRUCTURAL_PASS (5-product evaluations, 12-18 inline cites, 29-33 distinct URLs); Coder-Next was 0/3 STRUCTURAL_FAIL. Internet-research workflows aren't hopeless for local models — they're a 27B strength, just not Coder-Next's. (Citation validity is hand-grading placeholder; this is structural completion only.)
- **Coder-Next has a real hallucination-resistance gap.** Adversarial-hallucination: 27B 3/3 100% accurate / 0 dangerous; Coder-Next 1/3 with the one ship-attempt landing 2 confirmed-fabrications-as-real (right at the safety threshold). Same failure shape as the documented dreamserver-1-pr-audit Coder-Next variance.
- **Cost-per-attempt: Coder-Next is 4-12× cheaper** when it ships. When it doesn't ship (stuck-detector cases), it spends 25+ minutes and ~$0.03 producing nothing, which inverts the economics for hallucination-resistance-required tasks.
- **Both miss multi-week risks on PM-synthesis.** Project management: workstream + decision recall is excellent (6/6 + 3-4/4 every run for both models), but risks 2-3/6 across all runs and both models — multi-week-spanning risks systematically dropped.

---

## What the data supports

**Strong claims:**
- Cloud entries (Opus-4.7, GPT-5.5) reliably ship complete deliverables on all three benchmarks. Local 30B-class quantized entries do not.
- **Spec-compliance and verdict-accuracy are different axes.** On `dreamserver-1-pr-audit`, Coder-Next has 100% spec compliance and 33% factual accuracy. 27B has 0% spec compliance (no `verdict.md`) and 100% factual accuracy in the implicit verdicts present in `review.md`. From the artifact alone you can't tell which mode you're in for any given Coder-Next run; the wrong runs include fabricated evidence (line citations to non-existent issues, fake test scripts).
- **Cost-per-attempt at N=1**: Coder-Next is ~4× cheaper than 27B. For an ensemble-with-verification deployment shape, the economics favor running Coder-Next 3+ times and verifying than running 27B once.
- **35B-A3B-AWQ at 4-bit is below the floor** for these tasks: 0 of 3 wallstreet attempts shipped; 0 of 1 dreamserver-1-pr-audit attempts shipped. Higher-precision quantizations untested.

**Weaker / not-yet-supported:**
- "Coder-Next is X% wrong on PR review in general" — current evidence is 2/3 wrong on a single PR. Need more PRs and more N to pin a real rate.
- "27B is reliably better than Coder-Next for analytical work" — likely true but evidence is qualitative (the 3 hand-written reviews on `dreamserver-75-pr-audit/Qwen3.6-27B-AWQ/` are clean; 27B's `review.md` content on PR #1057 is excellent). Phase 3 hand-grading sharpens this: 27B prose quality 5/5 on doc-synthesis, business-memo bias-pushback 5/5; Coder-Next 4/5 on the same axes.
- "Cloud models are N× better than local on this benchmark" — categorical gap is clear (cloud ships, local mostly doesn't), but per-claim accuracy for the cloud entries isn't graded with the same methodology used on the local entries.
- "27B citations on the market-research microbench are valid" — sampled 18 of 33 URLs (~55%) validated. 86% mostly-valid / 64% strict-valid out of 14 testable URLs (4 were inaccessible to the validator from this IP). Measured `citations_valid_pct = 75`. **Important nuance: factual content (prices, certifications) is 100% accurate in the validated sample; the error mode is URL drift, not fabrication.** The remaining 15 URLs are unverified — sample is large enough to assert *most* citations are valid but not "all 33."

---

## Model selection guide

> The recommendations below are conditional on the task class this benchmark covers — long-horizon agentic work, structured deliverables, real-world-shaped tasks. They don't speak to interactive chat, single-question Q&A, or coding completion. For those, this benchmark has no signal.

### Choosing between 27B and Coder-Next: pick by task class

**Aggregate pass rate is identical** (20/36 each on the microbench). The two models are not interchangeable but they are also not strictly ranked — they have complementary task-class strengths. The selection criterion is therefore "which task class is this?" rather than "which model is generally better?"

| If your task is... | Pick | Why |
|---|---|---|
| Adversarial review / fabrication-resistance / security audit | **27B** | 3/3 PASS at 100% accuracy / 0 dangerous on adversarial-hallucination; Coder-Next 1/3 with 2 fabrications-as-real on the shipping run |
| Internet research with sustained multi-step workflows | **27B** | 3/3 STRUCTURAL_PASS on market-research; Coder-Next 0/3 STRUCTURAL_FAIL |
| Bug-fixing / code-task with running tests | **27B** | 3/3 vs 2/3; only marginal. Coder-Next is 1.6× faster — pick by speed if you don't care about the marginal reliability |
| Doc synthesis / business memo / writing rewrite / PM synthesis | **Coder-Next** | Wins on doc-synthesis (2/3 vs 0/3 — 27B can't trim to word limits), business-memo (3/3 vs 2/3), writing (2/3 vs 0/3 — 27B's customer-email subdimension fails), PM (1/3 vs 0/3) |
| Tight-schema structured extraction / triage / classification | **Either** (lean Coder-Next for cost) | Both 3/3; 27B more accurate (100% on 20 fields vs ~92%); Coder-Next 4-12× cheaper |
| CI failure debugging | **Either** (lean Coder-Next for cost) | Both 3/3 clean; Coder-Next ~2× cheaper |
| Cost is binding | **Coder-Next** | 4-12× cheaper per attempt on Phase 2 cells when both ship; 5.6× faster on business-memo, 7× on writing/editing, 4.3× on PM |
| Speed is binding | **Coder-Next** | 2-5× faster wall on every cell where both ship |

**One sentence recommendation:** *Pick by task class using the table above; default to Coder-Next when the task class is ambiguous or cost matters; default to 27B when fabrication-resistance or sustained-research is the binding requirement.*

### Detail: when to use **Qwen3.6-27B-AWQ**

- **Hallucination resistance is required.** The single sharpest local-model superiority signal in this repo: on the adversarial-hallucination microbench (15 issues, 6 real / 9 fabricated, agent must classify), 27B was 3/3 PASS with 100% accuracy and 0 dangerous errors; Coder-Next was 1/3 PASS with 2 confirmed-fabrications-as-real on the one shipping run. For security review, factual research, anything where confidently-wrong is dangerous, 27B is the pick.
- **Internet-research-driven workflows.** The second-sharpest local-model superiority signal: market-research microbench saw 27B 3/3 STRUCTURAL_PASS (5 products, 12-18 inline cites to 29-33 distinct URLs) and Coder-Next 0/3 STRUCTURAL_FAIL. 27B drives sustained multi-step research that Coder-Next doesn't. Caveat: STRUCTURAL_PASS only — sample-grade citations rather than consuming blind.
- **Tight-schema structured tasks.** 27B was 100% on 20-field extraction across 3 runs, 100% duplicate-cluster recall on triage, 12/12 PASS on Phase 2 programmatic graders. The "27B doesn't ship" framing from the dreamserver-PR-audit benchmark turned out to be task-class-specific (unbounded markdown narrative). When the deliverable shape is constrained, 27B ships cleanly.
- **Human-in-the-loop review work where intermediate analysis matters more than spec-compliant deliverables.** 27B's `review.md` and `research/questions.md` content was the highest-quality across all six N=1 runs on PR #1057. A reviewer reading that as research notes would get a substantively correct read on the catalog-handling distinction.
- **Tasks where truthfulness matters more than artifact obedience.** 27B's failures are usually "didn't finish" or "didn't write the spec-required file"; it doesn't fabricate confident-but-wrong claims with citations.
- **Tasks where you control the downstream consumption.** If your pipeline expects markdown notes (not a structured `verdict.md` JSON), 27B's output is usable as-is.

### Detail: when to use **Qwen3-Coder-Next-AWQ**

- **Pipelines where artifact shape is required and a verifier exists.** If your downstream consumes `verdict.md`/`tag`/`done()` and you have a separate check for correctness (a second model, a human pass, regression tests), Coder-Next ships reliably and is ~4× cheaper than 27B.
- **Bounded business-memo, triage, and writing-rewrite tasks.** Coder-Next was 3/3 PASS on business-memo (bias-signal recall), 3/3 PASS on triage at 96.7% category accuracy (better than 27B's 86.7%), 2/3 PASS on writing-editing. Below the cost-per-attempt of 27B by 4-12× and competitive on accuracy.
- **Ensemble-with-verification setups.** Run Coder-Next 3-5 times on the same input, take majority vote, flag dissent for human review. The variance characteristic is documented; you can build around it.
- **Time-to-output matters.** ~3 min/attempt at N=1 vs ~7 min for 27B. If artifact completion + speed beats verdict-accuracy in your loss function, Coder-Next is the pick.

### When to **avoid both** local models

- **Single-shot autonomous high-stakes verdicts** (security review, financial recommendations consumed without verification, anything cited downstream). Coder-Next's fabrication risk is documented; 27B's no-ship risk means the verdict you'd cite isn't there in machine-readable form.
- **Long-horizon (>30 min) unattended work.** Both models find degenerate failure modes within 30-60 minutes on the 75-PR task. Coder-Next loops; 27B Goodharts the spec or hits the per-response token cap.
- **Internet-research-driven workflows on Coder-Next specifically.** Coder-Next was 0/3 STRUCTURAL_FAIL on the market-research microbench (stuck-in-research, api-error). 27B does fine on the same task — see "When to use 27B" above. If you only have Coder-Next, have a human gather sources first.
- **Tasks where fabricated-but-plausible technical claims are dangerous.** If a wrong cited line number or invented test would mislead someone with cleanup cost > the win from automation, don't use Coder-Next single-shot. 27B is safer here, but its no-ship failure means the real review work has to be done by hand.

### When to use **Qwen3.6-35B-A3B-AWQ**

- The current evidence in this repo argues against using it for this task class. 0 of 3 wallstreet attempts shipped; 0 of 1 PR-audit attempts produced any artifact. Higher-precision quantizations might help; 4-bit AWQ at 3B active params doesn't clear the floor.

### When to use **cloud (Opus-4.7 / GPT-5.5 class)**

- **Long-horizon autonomous work where correctness matters and verification budget is limited.** Both cloud entries shipped complete deliverables on all three benchmarks. The categorical gap to local is large — we observed local-model fabrication and incomplete deliverables across local entries; cloud entries didn't show those failure shapes.
- **Tasks where artifact completion is non-negotiable.** Cloud entries reliably produce the spec-shaped output. Local entries don't.
- This said, **the cloud entries here aren't graded with the same per-claim methodology used on the local entries** (see KNOWN-LIMITATIONS § comparison-to-cloud). The cloud-vs-local gap is currently established at the *categorical* level (shipping vs not), not at the per-claim accuracy level.

---

## What would change this picture

These additions would tighten the recommendations above; until they land, the recommendations are best read as "based on this evidence" rather than "definitive":

1. **Validate the remaining 15 unsampled URLs and the 4 inaccessible-from-this-validator URLs** on the 27B market-research entry. Currently 18/33 sampled, measured citations_valid_pct = 75. The 4 inaccessible URLs (PCMag, ZDNet, two LastPass pages) are blocked by Cloudflare from the validator's IP — they could be sampled from a different IP, or the agent's specific cited content could be cross-referenced from archive.org. Would tighten the measured number from 75 (sample) to a fully-measured rate.
2. **Per-claim rubric applied uniformly** to cloud entries. Phase 3 hand-grading is now done for the local entries (prose, stance, source skepticism, balance, citations, tone fit, faithfulness, fabrication count); cloud entries (Opus-4.7, GPT-5.5) on the older benchmarks haven't been graded with the same rubric. Would let cloud-vs-local comparisons go beyond "shipping vs not."
3. **Failed-run artifacts published** (receipts + transcripts for the 5+ unsuccessful local-model runs not currently in MMBT). Would let a reader see expected failure modes per model.
4. **N=10+ on the highest-signal cells** (Coder-Next on `dreamserver-1-pr-audit`, 27B on the same; both on `microbench-2026-04-28/adversarial-hallucination`). Would bound the variance the current N=3 only suggests.
5. **Different PR shapes** in the dreamserver-1-pr-audit family — the current PR has subtle architectural distinctions; a docs-only PR or a security PR would test different failure modes.
6. **Higher-precision quantizations** of the same models (FP8, BF16). Particularly for 35B-A3B which fails at 4-bit; might be a quantization-headroom issue rather than a base-model issue.

None of these are in scope for the current MMBT publication. They're separate experiments.
