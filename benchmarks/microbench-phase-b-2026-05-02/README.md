# microbench-phase-b-2026-05-02 — N=10 expansion + 27B-no-think third arm

> **How this entry relates to [`microbench-2026-04-28`](../microbench-2026-04-28/)**: this entry is the *current* picture for the 4 differential cells (p2_hallucination, p3_business, p3_doc, p3_market) at N=10 across all three model arms, and the *first* picture for 27B-no-think across the full 12-family grid (N=10). The 2026-04-28 entry remains the current N=3 baseline for the other 8 cells on Coder-Next + 27B-thinking — it is **not superseded**, and many cross-references in this entry point back to it. **Read both for the full picture.**
>
> **Of the ~240 runs in this batch, this entry publishes one representative run per (cell × model arm) — 22 representatives total.** Per-run artifacts (cost.json / grade.json / label.json / summary.json / receipt.json) for the remaining ~220 runs live on the source bench's `submit/phase-b-overnight-2026-05-02` branch (sibling branch in this repo), which preserves the full transcripts + workspace tarballs for reproducibility.
>
> **For the head-to-head comparison this enables, see [`../../COMPARISON.md`](../../COMPARISON.md).**
>
> ---
>
> Bumps the [`microbench-2026-04-28`](../microbench-2026-04-28/) sample size from N=3 → N=10 on the four highest-signal task families, and adds **27B-no-think** (`--no-think` flag, no other changes) as a third arm across the **full 12-family grid**. Together, ~240 runs across three models.

## How to read this entry

This entry has multiple docs and many small lean-entry directories. Suggested reading order:

1. **Start with [`findings.md`](findings.md)** — the consolidated cross-task writeup. Per-cell tables, Wilson CIs, cost analysis, the three identical-call-loop subclasses (`scroll-loop`, `word-trim-loop`, `rewrite-loop`), the "When to use which model" decision framework, and cross-references to prior MMBT entries.
2. **Drill into a specific cell** — every task family has its own directory (e.g., [`adversarial-hallucination/`](adversarial-hallucination/), [`market-research/`](market-research/), [`p3_doc → doc-synthesis/`](doc-synthesis/), etc.) with a per-cell README and one or more model-arm lean entries. The 4 differential cells (`adversarial-hallucination`, `business-memo`, `doc-synthesis`, `market-research`) have all three model arms represented.
3. **Read [`findings-pairwise-quality-three-model.md`](findings-pairwise-quality-three-model.md)** for hand-graded quality differences on the both-ship cells (`p2_ci`, `p2_extract`, `p2_triage`). **Includes a load-bearing correction to the 2026-04-28 study's `p2_ci` regression attribution.**
4. **The pathology lean entries under [`market-research/`](market-research/)** — `Qwen3.6-27B-AWQ-no-think-v1-scroll-loop`, `-v5-runaway-generation`, `-v8-scroll-loop`, plus Coder-Next's `-v1-stuck` and `-v3-api-error` — are the canonical examples for the new failure-mode entries in [`tooling/FAILURE-TAXONOMY.md`](../../tooling/FAILURE-TAXONOMY.md).
5. **For operators reproducing**: [`tooling/scripts/SUBSTANCE-MONITORING-WORKFLOW.md`](../../tooling/scripts/SUBSTANCE-MONITORING-WORKFLOW.md) is the substance-check workflow that surfaced the new pathologies. It saved ~5.8 GPU-hours on this chain alone (concrete numbers in `findings.md` § "Operator-monitoring ROI").

## What this entry is

Two distinct experiments, presented together because the data complements:

1. **Phase B (2026-04-30 → 2026-05-02)** — bumped `p2_hallucination`, `p3_business`, `p3_doc`, `p3_market` from N=3 to N=10 for both 27B-thinking and Coder-Next. Goal: bound the headline failure rates from `microbench-2026-04-28` with proper Wilson CIs.
2. **27B-no-think full grid (2026-05-01 → 2026-05-03)** — ran 27B with `--no-think` across all 12 task families × N=10 = 120 runs. Goal: see whether disabling the thinking trace changes 27B's failure profile, especially on the `p3_doc` word-trim loop.

## Headline

| Model | Coverage | Ship rate (done_signal) | Wilson 95% CI |
|---|---|---:|---|
| Qwen3-Coder-Next-AWQ | 4 cells × N=10 + 8 cells × N=3 = 63 runs | 47/63 = 74.6% | [62.5%, 83.9%] |
| Qwen3.6-27B-AWQ (thinking) | 4 cells × N=10 + 8 cells × N=3 = 62 runs | 46/62 = 74.2% | [62.0%, 83.7%] |
| Qwen3.6-27B-AWQ (no-think) | **12 cells × N=10 = 118 graded + 2 op-labeled = 120** | **113/118 = 95.8%** | [90.5%, 98.2%] |

**On the 4 differential cells where all three models have N=10:**

| Cell | Coder-Next | 27B (thinking) | 27B (no-think) |
|---|---|---|---|
| p2_hallucination | 5/10 | 7/10 | **10/10** |
| p3_business | **10/10** | 9/10 | 8/10 |
| p3_doc | **10/10** | 6/10 | 8/10 |
| p3_market | 0/10 | 8/10 | 7/10 (+2 op-labeled scroll-loops) |
| **Subtotal** | **25/40** (62.5%) | **30/40** (75.0%) | **33/38** (86.8%) |

See [`findings.md`](findings.md) for the full per-cell breakdown, failure-mode distributions, and the substance-vs-liveness monitoring methodology that surfaced two new pathologies.

## Three high-signal findings

### 1. 27B-no-think rescues `p3_doc` from the word-trim loop

Phase B confirmed `p3_doc` 27B-thinking hits a stable ~40% `wall_killed_identical_call_loop` rate (4/10 runs) — the model writes a brief, counts words, sees it's over 700, edits, recounts, loops on the budget. **Disabling thinking drops the loop rate to 2/10.** Doc-synthesis ship rate goes from 6/10 (thinking) to 8/10 (no-think).

### 2. Coder-Next collapses on `p3_market` (0/10 done_signal)

Across 10 attempts at the live-network market-research task, Coder-Next ships zero. Failure mix: 5× `stuck_no_workspace_change_for_500_iters`, 4× `api_error: HTTP Error 400` (262K context overflow), 1× `wall_killed_low_progress_bash_loop`. 27B variants ship 7-8/10 on the same task. **For internet-research-driven workflows, 27B is the only viable local pick of the two.**

### 3. Two new pathologies for the taxonomy

The operator-monitoring run during the no-think grid surfaced patterns the harness's own stuck-detector misses:

- **Scroll-loop subclass of `identical-call-loop`** — model emits the same digit-stripped tool-call template 30+ iters in a row but with different numeric offsets per iter (`content[N:N+20000]` walks with N += 20000). Raw command hashes are unique, so the harness's content-hash same-content guard does NOT fire. Caught in `p3_market_27b-nothink_v1` (155-iter streak) and `_v8` (31-iter streak) before the harness's 500-no-progress threshold. Now folded into [`tooling/FAILURE-TAXONOMY.md`](../../tooling/FAILURE-TAXONOMY.md) as a `scroll-loop` sub-label.
- **`runaway-generation` — new primary** — model emits a single response exceeding the harness's max-output-tokens budget without stopping. No tool-call repetition; transcripts go silent for 10+ minutes while the harness is alive and vLLM is healthy. Distinct from `timeout`, `api-error`, and `identical-call-loop`. Caught in `p3_market_27b-nothink_v5` (137,855-token single response). Now in the taxonomy.

## What's published here

This is a **lean entry**, same convention as [`microbench-2026-04-28`](../microbench-2026-04-28/):

- [`findings.md`](findings.md) — the consolidated cross-task writeup, including the three-model rollup and per-cell tables with Wilson CIs.
- This README.

**Per-run artifacts (cost.json / grade.json / label.json / summary.json / receipt.json) are NOT mirrored here for the ~240 runs in this batch.** They are checked into the source bench's `submit/phase-b-overnight-2026-05-02` branch (sibling branch in this repo), which preserves the full transcripts + workspace tarballs for reproducibility. If a per-run lean entry is added later for individual high-signal runs (the operator-SIGTERM'd loops, the runaway-generation), it will be linked from `findings.md`.

The earlier `microbench-2026-04-28` entry is **not superseded** by this one — both are valid datapoints. This entry expands sample size on 4 cells and adds a third model arm; the existing entry remains the per-task-family deep-dive with full per-task READMEs and one-representative-run-per-model lean dirs.

## Cross-references

- [`findings.md`](findings.md) — the consolidated cross-task writeup with per-cell tables, Wilson CIs, cost analysis, and "When to use which model" guidance
- [`findings-pairwise-quality-three-model.md`](findings-pairwise-quality-three-model.md) — three-model pairwise quality study (extends `findings/2026-04-28-pairwise-quality-study.md` to add 27B-no-think; corrects the `p2_ci` regression attribution)
- [`microbench-2026-04-28/findings.md`](../microbench-2026-04-28/findings.md) — the N=3 baseline this drop expands
- [`tooling/FAILURE-TAXONOMY.md`](../../tooling/FAILURE-TAXONOMY.md) — updated with `scroll-loop` and `runaway-generation`
- [`KNOWN-LIMITATIONS.md`](../../KNOWN-LIMITATIONS.md) — applies to this entry as well; the harness-drift caveat below extends it
- `submit/phase-b-overnight-2026-05-02` branch — full per-run transcripts + tarballs

## Caveats

- **Ship rate ≠ PASS rate.** This entry reports `done_signal` rate. PASS rate (does the agent's output meet the per-task grading rubric?) is pending the batch-grader sweep against the no-think tarballs.
- **Harness drift across batches.** N=3 baselines (most P1 + P2 cells for 27B-thinking and Coder-Next) used harness file_sha256 `7698067...`; the no-think grid used `7ea9592...`. Within each batch the comparison is internally consistent. The 4 N=10 differential cells share a single harness across all three model arms.
- **Operator-SIGTERM'd runs.** 2 of the 27B-no-think `p3_market` runs (v1, v8) were operator-SIGTERM'd at 31-155 identical-template iters per the documented `>30 same-content writes` methodology rule. Their `label.json` files are present (in the sibling submit branch); their transcripts and partial workspaces are preserved; they have no `summary.json` or `workspace_final.tar.gz`. The 7/8 ship rate above counts only graded runs; including the labeled-as-loop runs gives 7/10 on `p3_market` 27B-no-think.
