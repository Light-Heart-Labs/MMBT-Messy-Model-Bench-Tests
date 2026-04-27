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

## What the data supports

**Strong claims:**
- Cloud entries (Opus-4.7, GPT-5.5) reliably ship complete deliverables on all three benchmarks. Local 30B-class quantized entries do not.
- **Spec-compliance and verdict-accuracy are different axes.** On `dreamserver-1-pr-audit`, Coder-Next has 100% spec compliance and 33% factual accuracy. 27B has 0% spec compliance (no `verdict.md`) and 100% factual accuracy in the implicit verdicts present in `review.md`. From the artifact alone you can't tell which mode you're in for any given Coder-Next run; the wrong runs include fabricated evidence (line citations to non-existent issues, fake test scripts).
- **Cost-per-attempt at N=1**: Coder-Next is ~4× cheaper than 27B. For an ensemble-with-verification deployment shape, the economics favor running Coder-Next 3+ times and verifying than running 27B once.
- **35B-A3B-AWQ at 4-bit is below the floor** for these tasks: 0 of 3 wallstreet attempts shipped; 0 of 1 dreamserver-1-pr-audit attempts shipped. Higher-precision quantizations untested.

**Weaker / not-yet-supported:**
- "Coder-Next is X% wrong on PR review in general" — current evidence is 2/3 wrong on a single PR. Need more PRs and more N to pin a real rate.
- "27B is reliably better than Coder-Next for analytical work" — likely true but evidence is qualitative (the 3 hand-written reviews on `dreamserver-75-pr-audit/Qwen3.6-27B-AWQ/` are clean; 27B's `review.md` content on PR #1057 is excellent). Not graded against a fixed rubric.
- "Cloud models are N× better than local on this benchmark" — categorical gap is clear (cloud ships, local mostly doesn't), but per-claim accuracy for the cloud entries isn't graded with the same methodology used on the local entries.

---

## Model selection guide

> The recommendations below are conditional on the task class this benchmark covers — long-horizon agentic work, structured deliverables, real-world-shaped tasks. They don't speak to interactive chat, single-question Q&A, or coding completion. For those, this benchmark has no signal.

### When to use **Qwen3.6-27B-AWQ**

- **Human-in-the-loop review work where intermediate analysis matters more than spec-compliant deliverables.** 27B's `review.md` and `research/questions.md` content was the highest-quality across all six N=1 runs on PR #1057. A reviewer reading that as research notes would get a substantively correct read on the catalog-handling distinction.
- **Tasks where truthfulness matters more than artifact obedience.** 27B's failures are usually "didn't finish" or "didn't write the spec-required file"; it doesn't fabricate confident-but-wrong claims with citations.
- **Tasks where you control the downstream consumption.** If your pipeline expects markdown notes (not a structured `verdict.md` JSON), 27B's output is usable as-is.

### When to use **Qwen3-Coder-Next-AWQ**

- **Pipelines where artifact shape is required and a verifier exists.** If your downstream consumes `verdict.md`/`tag`/`done()` and you have a separate check for correctness (a second model, a human pass, regression tests), Coder-Next ships reliably and is ~4× cheaper than 27B.
- **Ensemble-with-verification setups.** Run Coder-Next 3-5 times on the same input, take majority vote, flag dissent for human review. The variance characteristic is documented; you can build around it.
- **Time-to-output matters.** ~3 min/attempt at N=1 vs ~7 min for 27B. If artifact completion + speed beats verdict-accuracy in your loss function, Coder-Next is the pick.

### When to **avoid both** local models

- **Single-shot autonomous high-stakes verdicts** (security review, financial recommendations consumed without verification, anything cited downstream). Coder-Next's fabrication risk is documented; 27B's no-ship risk means the verdict you'd cite isn't there in machine-readable form.
- **Long-horizon (>30 min) unattended work.** Both models find degenerate failure modes within 30-60 minutes on the 75-PR task. Coder-Next loops; 27B Goodharts the spec or hits the per-response token cap.
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

1. **Per-claim rubric applied uniformly** to every entry (cloud + local). Hand-grade verdict correctness, line citations, fabricated-evidence count, etc., per a fixed scoring scheme. Would convert the "not graded" cells to numbers.
2. **Failed-run artifacts published** (receipts + transcripts for the 5+ unsuccessful local-model runs not currently in MMBT). Would let a reader see expected failure modes per model.
3. **N=10+ on the highest-signal cells** (Coder-Next on `dreamserver-1-pr-audit`, 27B on the same). Would bound the variance the current N=3 only suggests.
4. **Different PR shapes** in the dreamserver-1-pr-audit family — the current PR has subtle architectural distinctions; a docs-only PR or a security PR would test different failure modes.
5. **Higher-precision quantizations** of the same models (FP8, BF16). Particularly for 35B-A3B which fails at 4-bit; might be a quantization-headroom issue rather than a base-model issue.

None of these are in scope for the current MMBT publication. They're separate experiments.
