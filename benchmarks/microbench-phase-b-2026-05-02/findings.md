# 2026-05-02 — Phase B (N=10) + 27B-no-think across 12 task families

> Phase B bumped the 4 differential cells from N=3 → N=10 to bound the headline failure rates from `microbench-2026-04-28`. The 27B-no-think run is a third arm on the full 12-family grid (120 runs) that asks: does dropping the `<think>` trace change 27B's failure profile, especially on the doc-synthesis word-trim loop? Yes — and it also shifts the daily-driver picture.
>
> **Top-line rewrite of `microbench-2026-04-28`:**
>
> 1. **27B-no-think is the most reliable shipper of the three on like-for-like cells** (33/38 ≈ 86.8%, vs 30/40 = 75% for thinking-mode 27B and 25/40 = 62.5% for Coder-Next on the four N=10 differential cells).
> 2. **27B-no-think rescues `p3_doc` from the word-trim loop** — 8/10 ship vs 6/10 thinking.
> 3. **The `p3_doc` thinking-mode loop rate is now bounded** as a stable ~40% failure shape (4/10 wall_killed at N=10, Wilson 95% [16.8%, 68.7%]), not a v2/v3 fluke.
> 4. **Coder-Next's `p3_market` 0/3 STRUCTURAL_FAIL extends to 0/10** at N=10 — Wilson 95% [0%, 27.8%]. Confirmed reproducible failure shape.
> 5. **Coder-Next's `p2_hallucination` 1/3 PASS hint extends to 5/10 stuck** at N=10 — bounded as a real ~50% failure shape, not a 1-of-N flake.

## What was tested

### Phase B (N=10 expansion)

| Cell | 27B (thinking) | 27B (no-think) | Coder-Next |
|---|---|---|---|
| p2_hallucination | 10 | 10 | 10 |
| p3_business      | 10 | 10 | 10 |
| p3_doc           | 10 | 10 | 10 |
| p3_market        | 10 | 10 | 10 |

### 27B-no-think full grid

| Cell | 27B (thinking) — for comparison | 27B (no-think) | Coder-Next — for comparison |
|---|---|---|---|
| p1_bugfix         | 3  | **10** | 2 |
| p1_refactor       | 3  | **10** | 3 |
| p1_testwrite      | 3  | **10** | 3 |
| p2_ci             | 3  | **10** | 3 |
| p2_extract        | 3  | **10** | 3 |
| p2_triage         | 3  | **10** | 3 |
| p3_pm             | 3  | **10** | 3 |
| p3_writing        | 3  | **10** | 3 |

(N=3 cells inherit from the `microbench-2026-04-28` baseline.)

## Headline ship rates by model

| Model | done_signal | Total graded | Rate | Wilson 95% CI |
|---|---|---|---|---|
| Qwen3-Coder-Next-AWQ | 47 | 63 | 74.6% | [62.5%, 83.9%] |
| Qwen3.6-27B-AWQ (thinking) | 46 | 62 | 74.2% | [62.0%, 83.7%] |
| Qwen3.6-27B-AWQ (no-think) | **113** | **118** | **95.8%** | [90.5%, 98.2%] |

The 27B-no-think aggregate is inflated by the 70 P1+P2 runs where it scored 100%. The fair like-for-like measure is the 4 N=10 differential cells, which removes the P1+P2 inflation:

| Model | done_signal on 4 differential cells | Rate |
|---|---|---|
| Coder-Next | 25/40 | 62.5% |
| 27B (thinking) | 30/40 | 75.0% |
| **27B (no-think)** | **33/38** | **86.8%** |

(`p3_market_27b-nothink` denominator is 38 because 2 runs were operator-SIGTERM'd at >30 identical-template iters and have label.json instead of summary.json. Including them gives 33/40 = 82.5%.)

## Per-cell results

### Phase 1 — coding tasks (programmatic graders)

| Cell | Coder-Next | 27B (thinking) | 27B (no-think) |
|---|---|---|---|
| p1_bugfix    | 2/2 done_signal | 0/3 done_signal* | **10/10** done_signal |
| p1_refactor  | 3/3 done_signal | 1/3 done_signal* | **10/10** done_signal |
| p1_testwrite | 2/3 done_signal | 0/3 done_signal* | **10/10** done_signal |

`*` 27B-thinking N=3 baselines used an older harness sha. The 1/9 P1 ship rate may include harness-related effects; see Caveats. Re-running these on the current harness is on the follow-up list.

### Phase 2 — structured business tasks (programmatic graders)

| Cell | Coder-Next | 27B (thinking) | 27B (no-think) |
|---|---|---|---|
| p2_ci             | 3/3 done | 3/3 done | **10/10** done |
| p2_extract        | 3/3 done | 3/3 done | **10/10** done |
| p2_hallucination  | 5/10 done (5/10 stuck) | 7/10 done | **10/10** done |
| p2_triage         | 3/3 done | 3/3 done | **10/10** done |

**`p2_hallucination` ship-rate breakdown (N=10):**
- Coder-Next: 5/10 done_signal, 5/10 `stuck_no_workspace_change_for_500_iters`. The model can't decide cleanly between "real" and "fabricated" issues across the 6-real-9-fabricated set; runs out the workspace-hash budget reading code without writing a verdict. Wilson 95% [23.7%, 76.3%].
- 27B-thinking: 7/10 done_signal. Higher than Coder-Next's stuck rate but with N=10 not strong enough to call this a clean win.
- 27B-no-think: **10/10 done_signal**. Cleanest of the three on this task.

### Phase 3 — unbounded business/writing (mix of programmatic + hand-grading)

| Cell | Coder-Next | 27B (thinking) | 27B (no-think) |
|---|---|---|---|
| p3_business | **10/10** done | 9/10 done (1 wall_killed) | 8/10 done (2 wall_killed identical-call-loop) |
| p3_doc      | **10/10** done | 6/10 done (4 wall_killed identical-call-loop) | **8/10** done (2 wall_killed identical-call-loop) |
| p3_market   | 0/10 done (5 stuck, 4 api_error, 1 wall_killed) | 8/10 done | 7/10 done (1 runaway-generation, 2 op-labeled scroll-loop) |
| p3_pm       | 3/3 done | 3/3 done | **10/10** done |
| p3_writing  | 3/3 done | 3/3 done | **10/10** done |

**`p3_doc` is the most interesting cell.** Phase B confirmed 27B-thinking has a stable ~40% rate of `wall_killed_identical_call_loop` on this task (4/10 runs). The pattern: the model writes a draft, counts words, sees it's over 700, edits, recounts, loops on the budget constraint. With thinking disabled, the loop rate drops to 2/10 — the model writes once and ships rather than iterating on word-count compliance. The trade-off (worth a follow-up PASS-rate analysis): the no-think briefs may exceed 700 words more often than thinking-mode's polished output. Ship rate climbs; PASS rate may not.

**`p3_market` is a mess for all three models.** Coder-Next: 0/10. 27B-thinking: 8/10 done but 2 of those originally were `api_error: timed out` that the chain orchestrator retried. 27B-no-think: 7/10 done + 1 `runaway-generation` (137K-token single response) + 2 operator-SIGTERM'd `scroll-loops` (155-iter and 31-iter streaks of the same PCMag-pricing scrape with only the page-slice offset changing). **Three distinct pathologies in 10 runs for one cell — only seen for 27B-no-think on `p3_market`.**

## Failure-mode distribution by model

| Failure mode | Coder-Next | 27B (thinking) | 27B (no-think) |
|---|---:|---:|---:|
| `wall_killed_identical_call_loop` | 0 | 5 | 4 |
| `wall_killed_low_progress_bash_loop` | 2 | 0 | 0 |
| `stuck_no_workspace_change_for_500_iters` | 9 | 0 | 0 |
| `model_stopped` (floor-failure) | 0 | 11* | 0 |
| `model_exceeded_max_tokens_*` (runaway-generation) | 1 | 0 | 1 |
| `api_error: HTTP Error 400` (context overflow) | 4 | 0 | 0 |
| operator-SIGTERM `scroll-loop` | 0 | 0 | 2 |

`*` Most `model_stopped` instances are on N=3 P1 baselines run on the older harness sha; the rate may be inflated by harness-related effects, not pure model behavior.

Each model has a *signature* failure profile:

- **Coder-Next**: dominant failures are `stuck_no_workspace_change_for_500_iters` and `api_error: HTTP Error 400` — the model gets stuck reading code without writing artifacts, or fills the 262K context budget without converging.
- **27B-thinking**: dominant failure is `wall_killed_identical_call_loop` — the model gets caught in word-budget retry loops on tasks with tight output constraints.
- **27B-no-think**: also `identical-call-loop`, but the manifestation is different — the *scroll-loop subclass* where the model walks an HTML response in fixed-byte slices looking for an answer it can't find. Plus one `runaway-generation` on `p3_market_v5`.

## Two new pathologies surfaced

The operator-monitoring window in the final ~3 hours of the no-think run caught two patterns the harness's stuck detector misses:

### `scroll-loop` (sub-label of `identical-call-loop`)

In `p3_market_27b-nothink_v1`, the model emitted the same 758-character bash command for **155 consecutive iterations** (iters 74-228), differing only by the Python slice offset (`content[2615000:2635000]` → `content[2795000:2815000]`, +20000 per iter). The model was walking PCMag's `best-password-manager-for-business` HTML response in 20KB-byte windows looking for LastPass pricing it couldn't find.

**Why the harness's same-content guard didn't fire:** the workspace-hash check fires after 500 iterations of unchanged workspace state. With each scroll iter producing different stdout content (different page slice), the hash *does* technically change — even though no real progress is being made. Raw command hashes are also all unique because the offsets differ.

**The fix:** digit-strip the recent tool-call commands before comparing. Iterations 74-228 of v1 collapse to *one* unique digit-stripped template. Tail-streak ≥ 30 of the same digit-stripped template is now the operator's SIGTERM trigger per the documented `>30 same-content writes` methodology rule. Folded into `tooling/FAILURE-TAXONOMY.md` as a sub-label.

The same pattern showed up in `p3_market_27b-nothink_v8` at 31 iters and likely in the 4 wall_killed_identical_call_loop runs in `p3_business` and `p3_doc` (those reached the harness's 500-no-progress before any operator could detect it).

### `runaway-generation` (new primary)

In `p3_market_27b-nothink_v5`, the model went silent at iter 67 — no new tool calls, no stuck-detector firing, transcripts stale for 17+ minutes despite the harness alive and vLLM healthy on port 8002. When the run finally finished, the finish_reason was `model_exceeded_max_tokens_137855` — a single model response that exhausted the harness's 137,855 output-token budget without stopping. No tool-call repetition because the model never emitted another tool call after the runaway response began.

This is distinct from `timeout` (HTTP didn't fire — well under the 3600s limit), `api-error` (vLLM returned a successful long response), and `identical-call-loop` (no tool-call repetition). Now `runaway-generation` is a primary label in `tooling/FAILURE-TAXONOMY.md`.

## When to use which model — updated

Carrying forward [`microbench-2026-04-28/findings.md`](../microbench-2026-04-28/findings.md)'s framing, with the Phase B + no-think findings folded in:

### When to use 27B-no-think (new)

- **Default for most non-coding tasks at N=10 ship-rate grain.** 27B-no-think hits 95.8% across the full grid and 86.8% on the 4 hardest cells. If you're picking a single local model for a bulk run and you're not specifically trying to extract a polished narrative, no-think 27B ships more reliably than thinking-mode.
- **Doc synthesis with a tight word limit.** Drops the word-trim loop rate from 4/10 → 2/10 vs thinking-mode. Caveat: the briefs may exceed the limit more often (PASS rate vs ship rate trade pending grader sweep).
- **Anything where you'd otherwise pick 27B-thinking** — no-think edges or matches it on every cell tested at N=10 except `p3_business` (8/10 vs 9/10 — within sampling noise).

### When 27B (either mode) is still required

- **Internet-research workflows.** `p3_market` at 7-8/10 ship for 27B variants vs 0/10 for Coder-Next. If you only have Coder-Next and you need market research, gather sources first by hand. (Within the 27B variants, thinking edges no-think 8/10 vs 7/10 — but the no-think failures cluster as scroll-loops that an operator can detect and SIGTERM, which is operationally cleaner than the harness running 500 iters before failing.)
- **Hallucination resistance at N=10.** 27B-no-think 10/10, 27B-thinking 7/10, Coder-Next 5/10. No-think wins, but both 27B variants beat Coder-Next.

### When Coder-Next is still the right choice

- **`p3_business` business memo at N=10:** Coder-Next 10/10 vs 27B-thinking 9/10 vs 27B-no-think 8/10. Not a huge gap, but Coder-Next is the only one that ships every run at this sample size.
- **Speed-sensitive shippable work.** Coder-Next remains 2-5× faster than 27B (per `microbench-2026-04-28` cost table). If the task is in a family where Coder-Next ships reliably (`p3_business`, `p3_doc`, structured P2 tasks), it's still the throughput pick.

### Avoid

- **Coder-Next on `p3_market`** — 0/10 done_signal at N=10, Wilson 95% [0%, 27.8%]. Reproducible.
- **27B-thinking on `p3_doc`** if ship rate matters more than polish — 6/10. Use 27B-no-think instead.
- **27B-no-think on `p3_market`** without operator monitoring — 30% pathological rate (1 runaway, 2 scroll-loops). The scroll-loops in particular don't trip the harness's stuck detector for 30+ minutes.

## Recommended follow-ups

1. **PASS-rate grader sweep** on the no-think tarballs — promotes ship-rate findings to PASS-rate. Pending.
2. **Re-run N=3 P1 cells for 27B-thinking on the current harness** — definitively settle whether the 1/9 P1 ship rate is harness-drift or real model regression.
3. **Pairwise quality study extension** — add 27B-no-think as a third arm to the existing `pairwise-quality-study.md`.

## Caveats

- **Ship rate ≠ PASS rate.** This document reports `done_signal` rate. PASS rate analysis pending.
- **Harness drift across batches.** N=3 baselines used file_sha256 `7698067...`; the no-think grid used `7ea9592...`. The 4 N=10 differential cells share a single harness across all three model arms (consistent comparison). Cross-batch P1 numbers may include harness-related effects.
- **Operator-SIGTERM'd runs (2 of 27B-no-think `p3_market`)** are labeled `scroll-loop` in their `label.json` files (in the source bench's `submit/phase-b-overnight-2026-05-02` branch). They're counted as failures in this doc's denominators (hence 7/10 not 7/8 for the headline `p3_market` rate). Their transcripts are preserved; their `summary.json` and `workspace_final.tar.gz` are absent because operator-SIGTERM bypasses the harness teardown.
- **Wilson 95% CI** is conservative for small N; on the N=3 cells, CIs are wide and not reported here.
