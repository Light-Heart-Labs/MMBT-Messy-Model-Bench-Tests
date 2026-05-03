# Three-Model Rollup — 27B-thinking, 27B-no-think, Coder-Next

> Consolidated view across **all** runs on the bench (Phase A canonical batches + Phase B differential N=10 cells + the new no-think full grid). Data captured between 2026-04-26 and 2026-05-03 across 12 task families. Headline: 27B-no-think is the most reliable shipper on the bench, edging both 27B-thinking and Coder-Next on like-for-like cells; Coder-Next collapses on `p3_market`; 27B-no-think rescues `p3_doc` from 27B-thinking's word-limit-trim loop.

## Coverage matrix

| Cell             | 27B (thinking) | 27B no-think | Coder-Next |
|------------------|---------------:|-------------:|-----------:|
| p1_bugfix        |              3 |       **10** |          2 |
| p1_refactor      |              3 |       **10** |          3 |
| p1_testwrite     |              3 |       **10** |          3 |
| p2_ci            |              3 |       **10** |          3 |
| p2_extract       |              3 |       **10** |          3 |
| p2_hallucination |         **10** |       **10** |     **10** |
| p2_triage        |              3 |       **10** |          3 |
| p3_business      |         **10** |       **10** |     **10** |
| p3_doc           |         **10** |       **10** |     **10** |
| p3_market        |              8 |            8 |     **10** |
| p3_pm            |              3 |       **10** |          3 |
| p3_writing       |              3 |       **10** |          3 |
| **TOTAL graded** |         **62** |      **118** |     **63** |

**Bold = N=10 cell.** Cells at N=3 are baseline samples from the original 2x3x3 grid (2026-04-26). The four cells at N=10 across all three models — `p2_hallucination`, `p3_business`, `p3_doc`, `p3_market` — are the **differential cells** where Phase B bounded the headline failure rates. Two additional p3_market runs per model are operator-labeled `identical-call-loop` (2 of the 27B-thinking originals had `api_error: timed out` and were swept by the chain orchestrator; 2 of the 27B-no-think runs were operator-SIGTERM'd during this monitoring session).

## Top-line ship rates

| Model           | done_signal | total | rate    | Wilson 95% CI    |
|-----------------|------------:|------:|--------:|------------------|
| 27B (thinking)  |          46 |    62 |   74.2% | [62.0%, 83.7%]   |
| 27B no-think    |     **113** |   118 | **95.8%** | [90.5%, 98.2%] |
| Coder-Next      |          47 |    63 |   74.6% | [62.5%, 83.9%]   |

**27B-no-think ships at 95.8%, vs ~74% for both 27B-thinking and Coder-Next.** This is the headline. (Caveat: 27B-no-think's denominator includes 70 runs on P1+P2 cells where it scored 100% — easier task classes inflate the aggregate. See the like-for-like comparison below for the comparable measure.)

## Like-for-like — the 4 N=10 differential cells (all three models)

| Cell             | 27B (thinking) | 27B no-think | Coder-Next |
|------------------|----------------|--------------|------------|
| p2_hallucination | 7/10           | **10/10**    | 5/10       |
| p3_business      | 9/10           | 8/10         | **10/10**  |
| p3_doc           | 6/10           | **8/10**     | **10/10**  |
| p3_market        | 8/10           | **7/8***     | 0/10       |
| **Subtotal**     | **30/40**      | **33/38**    | **25/40**  |
| **Ship rate**    | 75.0%          | **86.8%**    | 62.5%      |

`*` p3_market 27B-no-think had 8 graded runs (2 operator-SIGTERM'd identical-call-loops are labeled separately and don't enter the ship-rate denominator above; including them produces 7/10 = 70%).

On the four hardest cells, **27B-no-think ships ~12pp better than 27B-thinking and ~24pp better than Coder-Next.**

## Per-cell winners and the picture they paint

| Cell             | Winner          | Margin              | Story                                                           |
|------------------|-----------------|---------------------|-----------------------------------------------------------------|
| p1_bugfix        | 27B-no-think    | 10/10 vs 0/3, 2/2   | Thinking-mode regressed to N=0 ship; no-think is solid          |
| p1_refactor      | 27B-no-think    | 10/10 vs 1/3, 3/3   | Same pattern: thinking-mode regression                          |
| p1_testwrite     | 27B-no-think    | 10/10 vs 0/3, 2/3   | Same pattern                                                    |
| p2_ci            | tie             | 10/10, 3/3, 3/3     | All three reliable                                              |
| p2_extract       | tie             | 10/10, 3/3, 3/3     | All three reliable                                              |
| p2_hallucination | 27B-no-think    | 10/10 vs 7/10, 5/10 | No-think handles the fabrication-detection task cleanly         |
| p2_triage        | tie             | 10/10, 3/3, 3/3     | All three reliable                                              |
| p3_business      | Coder-Next      | 10/10 vs 9/10, 8/10 | Coder edges by one run; both 27B variants hit `wall_killed`     |
| p3_doc           | Coder-Next      | 10/10 vs 6/10, 8/10 | But 27B-no-think rescues 2 runs from thinking's word-trim loop  |
| p3_market        | 27B variants    | 8/10, 7/10 vs 0/10  | Coder collapses; 27B-no-think also has 3 distinct pathologies   |
| p3_pm            | 27B-no-think    | 10/10 vs 3/3, 3/3   | All ship at full N where tested                                 |
| p3_writing       | 27B-no-think    | 10/10 vs 3/3, 3/3   | All ship at full N where tested                                 |

**Three families decide the comparison: `p2_hallucination`, `p3_doc`, and `p3_market`.** Everything else is either a tie or has too-small N to differentiate. Within those three:
- `p2_hallucination`: 27B-no-think wins (10/10) over 27B-thinking (7/10) and Coder-Next (5/10).
- `p3_doc`: Coder wins (10/10), 27B-no-think (8/10) > 27B-thinking (6/10).
- `p3_market`: 27B variants (~70-80%) >> Coder-Next (0/10).

## The two big mode-specific findings

### 1. 27B-no-think rescues `p3_doc`

The doc-synthesis task asks for a brief.md ≤700 words distilling 12 PRs of context. With thinking enabled, 27B falls into a **word-limit-trim loop** at a stable ~40% rate (4/10 wall_killed in Phase B). Disabling thinking drops that to 2/10 — a substantial improvement.

The mechanism: in thinking-mode, the model writes a draft, counts words, sees it's over, edits to trim, recounts (now under), expands a section, recounts (over again), retries — looping on the word-budget constraint. In no-think mode, the model writes once and ships, which produces a slightly less-polished but actually-shipped artifact more often. (PASS rate vs. ship rate is open here — the no-think briefs may exceed 700 words more often than thinking-mode's polished output. PASS-rate analysis is pending the grader sweep.)

### 2. Coder-Next collapses on `p3_market`

Market research (live-network research across 5 password-manager vendors with pricing/security/SSO/CLI evaluation) is the worst cell for Coder-Next: **0/10 done_signal**. The 10 runs distribute as:
- 5 `stuck_no_workspace_change_for_500_iters`
- 4 `api_error: HTTP Error 400: Bad Request` (context overflow — the model fills 262K context without converging)
- 1 `wall_killed_low_progress_bash_loop`

By contrast, 27B-thinking ships 8/10 and 27B-no-think ships 7/10 (with 2 operator-SIGTERM'd identical-call-loops + 1 `model_exceeded_max_tokens_137855` accounting for the 3 non-shipping runs). The same task is **manageable for 27B variants but unrecoverable for Coder-Next** — strong evidence that Coder-Next's tighter context budget and code-orientation hurt it on open-ended research.

## Pathology distribution by model

| Failure mode                              | 27B-thinking | 27B-no-think | Coder-Next |
|-------------------------------------------|-------------:|-------------:|-----------:|
| `wall_killed_identical_call_loop`         |            5 |            4 |          0 |
| `wall_killed_low_progress_bash_loop`      |            0 |            0 |          2 |
| `stuck_no_workspace_change_for_500_iters` |            0 |            0 |          9 |
| `model_stopped` (floor-failure)           |           11 |            0 |          0 |
| `model_exceeded_max_tokens_*`             |            0 |            1 |          1 |
| `api_error: HTTP Error 400`               |            0 |            0 |          4 |
| operator-SIGTERM `identical-call-loop`    |       (none) |            2 |     (none) |

Each model has a *signature* failure profile:
- **27B-thinking**: dominant failure is `model_stopped` / floor-failure (11 runs) — the model emits text and quits without committing artifacts. (Caveat: most `model_stopped` instances are in N=3 P1 baselines run on an older harness sha — see Caveats below.)
- **27B-no-think**: failures concentrate in `identical-call-loop` (4 harness-killed + 2 operator-killed) — the model loops on tool calls when a research task lacks a clear stopping criterion.
- **Coder-Next**: failures concentrate in `stuck_no_workspace_change_for_500_iters` (9) + `api_error: HTTP Error 400` (4) — the model gets stuck in long iterations without committing to artifacts, or fills context without converging.

## Methodology improvements caught during the no-think run

The no-think run included an operator-monitoring pass that surfaced two methodology gaps:

1. **Liveness ≠ progress.** The harness's `--stuck-threshold 500` workspace-hash check does not catch *scroll-loops* — runs where the model emits the same digit-stripped tool-call template 30+ times in a row but with different offsets (`content[N:N+20000]` walks). Raw command hashes differ; the workspace-hash detector ignores them. v1 (p3_market_27b-nothink) walked 155 consecutive identical-template iters before manual SIGTERM. The fix in monitoring: digit-strip tool-call commands and count distinct templates — `tail_streak >= 30` triggers SIGTERM per the documented methodology rule.
2. **`model_exceeded_max_tokens_*` is a new pathology not in `agent-pilot/FAILURE-TAXONOMY.md`.** v5 (p3_market_27b-nothink) emitted a single 137,855-token response (the harness's hard limit) without stopping. Distinct from `identical-call-loop` (no tool repetition), `timeout` (harness 3600s HTTP not reached), and `api-error` (vLLM returned a successful response). Recommend `runaway-generation` primary label or sub-label of `partial-no-spec-output`.

Both improvements are now folded into FAILURE-TAXONOMY.md (this commit).

## Caveats

- **Harness drift across batches.** N=3 baselines (2026-04-26 → 2026-04-28) used harness `7698067...`; Phase B used the same harness; the 2026-05-02 no-think grid used `7ea9592...`. Within each batch the comparison is internally consistent, but cross-batch quantitative comparisons (especially the `model_stopped` / floor-failure rate for 27B-thinking on P1) may include harness-related effects.
- **Ship rate ≠ PASS rate.** This rollup reports `done_signal` rate. PASS-rate analysis (does the agent's output meet the per-task grading rubric?) requires running the batch graders against the new tarballs and comparing to ground truth. Pending.
- **N=3 cells have wide CIs.** Most P1 + P2 cells are at N=3 for 27B-thinking and Coder-Next, so the apparent winners (e.g., 27B-thinking 0/3 on p1_bugfix, p1_testwrite) are directional but not bounded.
- **The 4 wall_killed identical-call-loop runs in p3_business and p3_doc** for 27B-no-think likely follow the same scroll-loop pattern as the operator-SIGTERM'd ones, but their full transcripts haven't been hand-audited.

## Recommended follow-ups

1. **PASS-rate grader sweep on the no-think tarballs** — promote ship-rate findings to PASS-rate. ~1 hour mostly waiting.
2. **Pairwise quality study extension** — the existing 2026-04-28-pairwise-quality-study.md compares 27B-thinking vs Coder-Next on shared tasks. Add 27B-no-think as a third arm. ~1-2 hours.
3. **Re-run N=3 P1 cells for 27B-thinking on the current harness** — definitively settle whether the 1/9 P1 ship rate is a harness artifact or a real model regression. ~1 hour.

## Files

- Findings docs (chronological):
  - `findings/2026-04-26-2x3x3-grid-consolidated.md` — original baseline
  - `findings/2026-04-28-coding-and-business-microbenches.md` — N=3 phase deepdive
  - `findings/2026-04-28-pairwise-quality-study.md` — 27B vs Coder-Next pair audit
  - `findings/2026-05-02-phase-b-n10-results.md` — Phase B bounded the four differential cells at N=10
  - `findings/2026-05-03-27b-nothink-grid-results.md` — full 12-family no-think grid at N=10
  - **this doc** — three-model rollup
- Per-run artifacts: `agent-pilot/logs/{cell}_{model}_v{N}/` (transcript + receipt + summary + tarball + label.json where applicable)
- Branch: `submit/phase-b-overnight-2026-05-02`
