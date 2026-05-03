# MMBT - Messy Model Bench Tests

This repository stores messy, real-world benchmark outputs from different
hardware and LLM tests in my lab.  It's my messy research, and exists for my personal use
but I'm making it public so that other people can use it too.

## Five-minute answers

| If you want to know… | Read |
|---|---|
| **"Coder-Next or 27B (or 27B-no-think) for my task?"** | [`COMPARISON.md`](COMPARISON.md) — head-to-head decision doc |
| The full single-table comparison across all entries | [`SCORECARD.md`](SCORECARD.md) |
| What this evidence can and can't support | [`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md) |
| How to benchmark a new local model | [`tooling/ADDING-A-MODEL.md`](tooling/ADDING-A-MODEL.md) |
| How to replay a specific past run | [`tooling/REPRODUCING.md`](tooling/REPRODUCING.md) |

## Operating point (read before quoting)

All published runs use **Cyankiwi 4-bit AWQ** quants on **2× RTX PRO 6000 Blackwell at 500 W cap**. Other quants (official FP8, Unsloth UD4 GGUF, BF16), other VRAM tiers (24 GB / 48 GB), other hardware classes (Mac M-series unified memory), and languages other than Python are **not characterized** here. See [`COMPARISON.md` § What this benchmark doesn't characterize](COMPARISON.md#what-this-benchmark-doesnt-characterize) for the full validity-boundary list, and [`ROADMAP.md`](ROADMAP.md) for what's queued to fill those gaps.

## Layout

```text
benchmarks/
  dreamserver-75-pr-audit/
    GPT-5.5/                   cloud, full audit
    Opus-4.7/                  cloud, full audit
    Qwen3.6-27B-AWQ/           local 30B-class, structurally complete + substantively partial
    Qwen3-Coder-Next-AWQ/      local MoE 80B/3B, no deliverable (failure-mode entry)
    findings-2026-04-27-local-models.md   cross-cutting writeup
  dreamserver-1-pr-audit/
    Qwen3-Coder-Next-AWQ/      local, single-PR deliverable (correct verdict, but variance-dominated — see entry README)
    Qwen3.6-27B-AWQ/           local, partial deliverable (excellent analysis, no verdict.md shipped)
    Qwen3.6-35B-A3B-AWQ/       local, floor failure (no artifacts produced)
  wallstreet-intern-test/
    GPT-5.5/                   cloud, full memo repo + board-of-advisors deck
    Opus-4.7/                  cloud, full memo repo
    Qwen3.6-27B-AWQ/           local, full memo repo (GTLB BUY, 1 of 3 runs shipped)
    Qwen3-Coder-Next-AWQ/      local, full memo repo (DOCU BUY, 1 of 3 runs shipped — verdict reliability caveat in README)
    Qwen3.6-35B-A3B-AWQ/       local, no usable deliverable (0 of 3 runs shipped, kept as failure-mode entry)
hardware-tests/
  vllm-power-sweep-2026-04-29/ rig characterisation: vLLM throughput vs GPU power cap, 28-cell sweep with raw CSVs + audit notes
```

## Benchmarks

| Benchmark | Prompt Shape | Model Entries |
|---|---|---|
| [`dreamserver-75-pr-audit`](benchmarks/dreamserver-75-pr-audit/) | Audit 75 open PRs in a live repository and produce a traceable maintainer triage repo. | `GPT-5.5`, `Opus-4.7`, `Qwen3.6-27B-AWQ`, `Qwen3-Coder-Next-AWQ` (failure-mode entry) |
| [`dreamserver-1-pr-audit`](benchmarks/dreamserver-1-pr-audit/) | Same task spec, scaled to a single PR. Built as the floor of an escalation ladder (1 → 2 → 4 → 8 → 16 → 32) to find each model's complexity ceiling. | `Qwen3-Coder-Next-AWQ`, `Qwen3.6-27B-AWQ`, `Qwen3.6-35B-A3B-AWQ` (floor failure) |
| [`wallstreet-intern-test`](benchmarks/wallstreet-intern-test/) | Build a traceable investment memo repo with raw sources, extracted data, a three-statement model, valuation, and recommendation. | `GPT-5.5`, `Opus-4.7`, `Qwen3.6-27B-AWQ`, `Qwen3-Coder-Next-AWQ`, `Qwen3.6-35B-A3B-AWQ` (failure-mode entry) |
| [`microbench-2026-04-28`](benchmarks/microbench-2026-04-28/) | 12 smaller-scope task families (5-30 min deliverables) split across 3 phases — coding (Phase 1), structured business tasks (Phase 2), unbounded business/writing (Phase 3). Designed to surface task-class-specific differences between local 30B-class quantizations. N=3 per cell. Three highest-signal task families published as full per-model entries: adversarial-hallucination, market-research, doc-synthesis. | `Qwen3.6-27B-AWQ`, `Qwen3-Coder-Next-AWQ` |
| [`microbench-phase-b-2026-05-02`](benchmarks/microbench-phase-b-2026-05-02/) | Bumps the four highest-signal cells of `microbench-2026-04-28` from N=3 → N=10 to bound the headline failure rates with proper Wilson CIs, and adds **27B-no-think** as a third arm across the **full 12-family grid** (~240 runs total). Settles the `p3_doc` 27B word-trim loop as a stable ~40% failure shape, and bounds Coder-Next's `p3_market` 0/3 STRUCTURAL_FAIL as 0/10 at N=10 (Wilson 95% [0%, 27.8%]). | `Qwen3.6-27B-AWQ` (thinking), `Qwen3.6-27B-AWQ` (no-think), `Qwen3-Coder-Next-AWQ` |

## Hardware tests

`hardware-tests/` holds rig characterisation runs — power, throughput, and thermal sweeps on the lab hardware itself, separate from agent-task benchmarks. They support the same evidence base (e.g. validating the operating power cap a model run was conducted under), but they live in their own tree because they answer hardware questions, not model questions.

| Test | Shape | What it measures |
|---|---|---|
| [`vllm-power-sweep-2026-04-29`](hardware-tests/vllm-power-sweep-2026-04-29/) | 7 GPU power caps × 5 min sustained vLLM load × 2 concurrencies (N=1, N=32) × 2 AWQ-INT4 models (Dense Qwen3.6-27B, MoE Coder-Next), 28 cells total, on RTX PRO 6000 Blackwell. | Throughput-vs-power-cap curve, native draw at unbounded cap, and per-cap thermal envelope. Validates the 500 W production cap (within 3.3 % of optimal in every scenario), and shows Coder-Next ≈ 1.8× faster batched / 2.3× faster single-stream than dense 27 B at every cap. The findings doc carries an "Audit notes" section flagging two per-cap "winner" markers that don't survive a re-read of the raw CSVs (a vLLM container warmup transient and a single-window thermal clock dip distort the per-cap winners without changing the plateau-shape headline). |

## At a glance

Two synthesis docs sit between this README and the per-entry detail:

- [`COMPARISON.md`](COMPARISON.md) — **head-to-head decision doc** for the three local model arms (Coder-Next vs 27B-thinking vs 27B-no-think). Organized by task class with cell-level evidence. Read this if your question is "which one should I use?"
- [`SCORECARD.md`](SCORECARD.md) — single-table summary across all entries (spec compliance, factual accuracy, fabricated-claim count, tests run, wall, cost upper bound, failure mode, "when to use which" guide). Read this if your question is "what's the full picture?"

Both link back to the per-entry artifacts they cite.

## Reproducing the runs

The [`tooling/`](tooling/) folder is the reproduction pack — agent harness, sandbox Dockerfile, vLLM launch commands, all 12 microbench task prompts, input starters, ground truth, grader scripts, and batch-runner scripts. With everything there plus a CUDA-capable Linux box and a HuggingFace model, an external reader can rerun any of the local-model entries here.

- **Replaying a published run**: see [`tooling/REPRODUCING.md`](tooling/REPRODUCING.md) — receipt-driven walkthrough.
- **Benchmarking a new local model**: see [`tooling/ADDING-A-MODEL.md`](tooling/ADDING-A-MODEL.md) — end-to-end guide with a four-command friendly path (`smoke_test.sh` → `run_microbench.sh` → `grade_microbench.sh` → `summarize.sh`). Half-day to one-day operator time per new model.

## How To Read A Model Entry

Start with the benchmark folder README, then open the model folder:

1. `benchmarks/<benchmark>/README.md`
2. `benchmarks/<benchmark>/<model>/README.md`
3. The model entry's README for its artifact-specific read order, then the main deliverables such as `report/` / `prs/` or `memo/` / `model/`.

For comparing multiple model entries within a benchmark, look for cross-cutting `findings-*.md` docs at the benchmark folder root (e.g. [`benchmarks/dreamserver-75-pr-audit/findings-2026-04-27-local-models.md`](benchmarks/dreamserver-75-pr-audit/findings-2026-04-27-local-models.md)).

## A note on "Messy"

The "Messy" framing is intentional. Some model entries are clean audits with traceable line-by-line reasoning (`Opus-4.7/` on the 75-PR task). Others are structurally-complete-but-substantively-partial scaffolds with a few hand-written reviews and 70+ template stubs (`Qwen3.6-27B-AWQ/` on the same task). Others are deliberate failure-mode entries with no audit artifacts at all but with documented failure trajectories ([`Qwen3-Coder-Next-AWQ/` on the 75-PR task](benchmarks/dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ/), [`Qwen3.6-35B-A3B-AWQ/` at N=1](benchmarks/dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/)).

**Before quoting any number from this repo, read [`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md).** It consolidates the caveats that affect what claims this evidence can support — small N, cherry-picked successes, dirty harness git SHAs, hand-graded inputs without a formal rubric, hardware specificity, the gap in cloud-vs-local apples-to-apples grading. Useful evidence; not yet a leaderboard.

This repository is licensed under [MIT](LICENSE). Third-party content (DreamServer code excerpts, SEC filings, cloud-LLM and local-model outputs, Cyankiwi quantizations) retains its original licensing — see [`NOTICE`](NOTICE).

The repo keeps the failures because the *kinds* of failure are themselves the comparison data. A reader picking a model for their own work needs to know that "this model can't complete this task" or "this model produces output shape without substance" — those are real properties of the model, not noise to filter out.

## Current Entries

**dreamserver-75-pr-audit:**
- [GPT-5.5](benchmarks/dreamserver-75-pr-audit/GPT-5.5/) — cloud, full audit (75 PRs, 34 merge / 40 revise / 1 reject)
- [Claude Opus 4.7 (1M context)](benchmarks/dreamserver-75-pr-audit/Opus-4.7/) — cloud, full audit (51 clean MERGE / 14 categorized HOLDs)
- [Qwen3.6-27B-AWQ](benchmarks/dreamserver-75-pr-audit/Qwen3.6-27B-AWQ/) — local, structurally complete (75/75 verdict files) but only 3 are real reviews; 72 are template stubs. Zero tests run.
- [Qwen3-Coder-Next-AWQ](benchmarks/dreamserver-75-pr-audit/Qwen3-Coder-Next-AWQ/) — local, **no audit deliverable** across 5 attempts. Three distinct degenerate failure modes (loops, cyclic-name slop, stuck-in-research). Folder kept as failure-mode evidence.
- [Cross-cutting findings doc](benchmarks/dreamserver-75-pr-audit/findings-2026-04-27-local-models.md) — comparison writeup of the local-model entries against the cloud entries

**dreamserver-1-pr-audit:**
- [Qwen3-Coder-Next-AWQ](benchmarks/dreamserver-1-pr-audit/Qwen3-Coder-Next-AWQ/) — local, single-PR deliverable, MERGE verdict (correct). **Caveat in README**: this is the cherry-picked correct run of three; other two gave REJECT (wrong, with fabricated technical issues).
- [Qwen3.6-27B-AWQ](benchmarks/dreamserver-1-pr-audit/Qwen3.6-27B-AWQ/) — local, partial deliverable. Best analytical content of any local-model run on this PR. No verdict.md shipped (failure to follow spec); implicit MERGE in `review.md`.
- [Qwen3.6-35B-A3B-AWQ](benchmarks/dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/) — local, **floor failure**. Zero artifacts produced; model investigated for 28 iters then stopped without writing.

**wallstreet-intern-test:**
- [GPT-5.5](benchmarks/wallstreet-intern-test/GPT-5.5/) — cloud, full memo repo + the follow-on board-of-advisors presentation in `board-of-advisors-presentation/`
- [Claude Opus 4.7 (1M context)](benchmarks/wallstreet-intern-test/Opus-4.7/) — cloud, full memo repo
- [Qwen3.6-27B-AWQ](benchmarks/wallstreet-intern-test/Qwen3.6-27B-AWQ/) — local, GitLab Inc. (`GTLB`) BUY recommendation. 1 of 3 attempts shipped (other 2: parser fault, 1-hour single-call timeout). 17 KB three-statement model, full audit trail.
- [Qwen3-Coder-Next-AWQ](benchmarks/wallstreet-intern-test/Qwen3-Coder-Next-AWQ/) — local, DocuSign (`DOCU`) BUY recommendation. 1 of 3 attempts shipped (other 2: scaffold-and-stop). 10.6 KB three-statement model. **Verdict-reliability caveat in entry README** — single-shot Coder-Next output can be confidently wrong with fabricated evidence (see PR-audit benchmark for documented examples).
- [Qwen3.6-35B-A3B-AWQ](benchmarks/wallstreet-intern-test/Qwen3.6-35B-A3B-AWQ/) — local, **no usable deliverable**. 0 of 3 attempts shipped. Folder kept as failure-mode evidence consistent with the model's PR-audit floor failure.

**microbench-2026-04-28:**
- [`adversarial-hallucination/`](benchmarks/microbench-2026-04-28/adversarial-hallucination/) — agent must distinguish 6 real bugs from 9 confident-but-wrong fabrications. Sharpest local-model superiority signal in the entire repo: 27B 3/3 PASS, Coder-Next 1/3 PASS with 2 confirmed-fabrications-as-real on the shipping run.
- [`market-research/`](benchmarks/microbench-2026-04-28/market-research/) — 5-product enterprise password manager comparison + pricing math + cited sources. Inversion of the prior "both fail at internet research" expectation: 27B 3/3 STRUCTURAL_PASS (12-18 cites to 29-33 distinct URLs), Coder-Next 0/3 STRUCTURAL_FAIL.
- [`doc-synthesis/`](benchmarks/microbench-2026-04-28/doc-synthesis/) — 1-page executive brief from 5 source documents, 700-word limit. Documents a 27B failure mode: 8/8 facts captured every run, but model can't trim to length (765-775 words across N=3, two runs entered identical-call-loops on `brief.md`).
- [`findings.md`](benchmarks/microbench-2026-04-28/findings.md) — cross-cutting writeup spanning all 12 task families (3 published full + 9 summarized).

**microbench-phase-b-2026-05-02:**
- [Qwen3-Coder-Next-AWQ](benchmarks/microbench-phase-b-2026-05-02/) — N=10 expansion across 4 differential cells. Headline: 0/10 STRUCTURAL_FAIL on `p3_market` (Wilson 95% [0%, 27.8%]) confirmed reproducible.
- [Qwen3.6-27B-AWQ (thinking)](benchmarks/microbench-phase-b-2026-05-02/) — N=10 expansion. Word-trim loop on `p3_doc` bounded as a stable ~40% failure shape (4/10 wall_killed).
- **[Qwen3.6-27B-AWQ (no-think)](benchmarks/microbench-phase-b-2026-05-02/) — new third arm**, full 12-family grid × N=10. 95.8% ship rate (Wilson 95% [90.5%, 98.2%]) — most reliable shipper of the three. Halves the `p3_doc` word-trim loop rate (4/10 → 2/10).
- [`findings.md`](benchmarks/microbench-phase-b-2026-05-02/findings.md) — full per-cell breakdown with Wilson CIs, three identical-call-loop subclasses, cost-per-shipped-run analysis, "when to use which" updates.
- [`findings-pairwise-quality-three-model.md`](benchmarks/microbench-phase-b-2026-05-02/findings-pairwise-quality-three-model.md) — hand-graded deliverable quality study; 27B-thinking and 27B-no-think substantively equivalent on shipped output.
