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

## All identical-call-loops are not the same — three subclasses

> Audit performed 2026-05-03 against the 6 `wall_killed_identical_call_loop` runs in this chain (4 in 27B-no-think + 2 in 27B-thinking) plus the operator-SIGTERM'd p3_market runs. The original audit hypothesis — that all `wall_killed_identical_call_loop` runs follow the `scroll-loop` pattern — was **wrong**. Three distinct subclasses turned up:

### Subclass 1 — `scroll-loop`
Model walks a data source in fixed-byte slices via repeated bash. Same tool template, different numeric offset per iter. Found in 2 runs:
- `p3_market_27b-nothink_v1` (155-iter streak): walking PCMag HTML response in 20K-byte slices for LastPass pricing
- `p3_market_27b-nothink_v8` (31-iter streak): same task, same template, different output filename per iter

This is the new pathology now in [`tooling/FAILURE-TAXONOMY.md`](../../tooling/FAILURE-TAXONOMY.md) as the `scroll-loop` sub-label.

### Subclass 2 — `word-trim-loop` (write-recount cycle)
Model alternates between writing the deliverable and counting its words, trying to satisfy the ≤700-word constraint. **Tool sequence is alternating** — single-template streak is low (often 1) but the digit-stripped *template count* over a 30-iter window is small (2-3 unique templates):

| Run | Last-30 template mix |
|---|---|
| `p3_business_27b-nothink_v5` | `15× write_file: memo.md` ⇄ `15× bash: wc -w memo.md` |
| `p3_doc_27b-nothink_v2` | `15× write_file: brief.md` ⇄ `15× bash: wc -w brief.md` |
| `p3_doc_27b-nothink_v6` | `10× write_file` + `10× wc -w` + `10× awk word-counter` |

This is the documented "27B word-limit-trim failure" from `microbench-2026-04-28/findings.md`. It manifests in both 27B-thinking (4/10 of the wall_killed `p3_doc` runs at N=10) and 27B-no-think (2/10 — the loop rate is *lower* without thinking but still nonzero).

### Subclass 3 — `rewrite-loop` (single-template-spam)
Model emits the same `write_file` or bash heredoc 30 times in a row, just re-rewriting the deliverable identically without any read or check between iters:

| Run | Last-30 template mix |
|---|---|
| `p3_business_27b-nothink_v7` | `30× bash: cat > /workspace/memo.md << 'ENDOFMEMO' # Executive Committee...` (same heredoc) |
| `p3_doc_27b_v2` | `30× write_file: /workspace/brief.md` (same content path, same content) |
| `p3_business_27b_v5` | `29× write_file: /workspace/memo.md` + 1 word-count call (essentially a degenerate word-trim) |
| `p3_doc_27b_v3` | `29× write_file: /workspace/brief.md` + 1 length check |
| `p3_doc_27b_v4` | `23× write_file: /workspace/brief.md` + 3 length checks |
| `p3_doc_27b_v6` | `26× write_file: /workspace/brief.md` + 2 word counts |

This pattern *would* be caught by the harness's content-hash same-content guard (because the writes are byte-identical), but it isn't, because the workspace state hash *does* technically advance per file write (the file is overwritten with the same content but the inode update is enough to dirty the workspace hash). It runs to the harness's 500-iter no-progress threshold instead.

### Detection coverage by subclass

The new [`tooling/scripts/check_substance.py`](../../tooling/scripts/check_substance.py) catches subclasses 1 and 3 via tail-streak ≥ 30 of the same digit-stripped template. **It does NOT catch subclass 2 (word-trim-loop) reliably** — that pathology has tail-streak = 1 (templates alternate). A future refinement could add a "low template diversity over a 30-iter window" check (e.g., ≤ 3 unique templates over 30 iters → flag) to catch alternating-pattern stuck-loops. Recommended methodology extension.

### Why subclasses matter

For decisions:
- **`scroll-loop`** is task-specific (web research with non-rendered content) and operator-detectable early (~iter 30 of streak → SIGTERM).
- **`word-trim-loop`** is a 27B-family pattern that thinking-mode amplifies — disabling thinking helps (4/10 → 2/10 on `p3_doc`) but doesn't eliminate. For tight word-budget tasks, expect a non-zero loop rate even with no-think.
- **`rewrite-loop`** is the catch-all pathology when the model has decided it's "done" but the harness disagrees. The model just keeps emitting the same deliverable. No methodology fix; needs a model-side improvement (e.g., better stop-token discipline).

## Cost and wall time

> All cost numbers are upper-bound estimates from `tooling/scripts/extract_cost.py` — wall time × power.limit (500 W cap on Tower2 since 2026-04-28) at $0.13/kWh residential rate. Real GPU draw is lower (idle between calls, peaks during decode) so these are *ceilings*, not point estimates. Use for *ranking*, not for absolute economics.

### Median wall and cost per run

| Cell | Coder-Next wall / cost | 27B (thinking) wall / cost | 27B (no-think) wall / cost |
|---|---|---|---|
| p1_bugfix         |    683 s / $0.0148 | 1078 s / $0.0233 | **2582 s** / $0.0466 |
| p1_refactor       |    322 s / $0.0070 |  322 s / $0.0070 | 562 s / $0.0101 |
| p1_testwrite      |    839 s / $0.0182 |  573 s / $0.0124 | 1186 s / $0.0214 |
| p2_ci             |     69 s / $0.0015 |  127 s / $0.0027 | 110 s / $0.0020 |
| p2_extract        |     17 s / $0.0004 |   71 s / $0.0015 |  49 s / $0.0009 |
| p2_hallucination  |    422 s / $0.0092 |  171 s / $0.0037 | 127 s / $0.0023 |
| p2_triage         |     62 s / $0.0013 |  197 s / $0.0043 | 154 s / $0.0028 |
| p3_business       |     31 s / $0.0006 |  163 s / $0.0035 | 171 s / $0.0031 |
| p3_doc            |     37 s / $0.0007 | 1113 s / $0.0201 | 144 s / $0.0026 |
| p3_market         |   2294 s / $0.0435 | 1720 s / $0.0330 | 2277 s / $0.0411 |
| p3_pm             |     16 s / $0.0003 |   80 s / $0.0017 |  68 s / $0.0012 |
| p3_writing        |     24 s / $0.0005 |  166 s / $0.0036 | 125 s / $0.0023 |

Three patterns from the medians:

1. **Coder-Next is dramatically faster on the cheap-task cells** — 5-10× faster than either 27B variant on `p3_business`, `p3_doc`, `p3_pm`, `p3_writing`, `p2_extract`. When a task is well-bounded and Coder-Next can ship it, throughput economics favor Coder-Next by an order of magnitude.
2. **No-think doesn't always reduce wall time vs thinking-mode.** On most cells it's faster (or tied), but on `p1_bugfix` and `p1_testwrite` it's actually 2× slower. The mechanism: thinking-mode 27B fails fast (`model_stopped` at low iter count) on those cells, while no-think 27B works through to a full `done_signal` over many iters. Faster-because-failed isn't a win; the 27B-no-think wall is the real "doing the task" wall.
3. **`p3_market` is expensive for everyone.** All three models spend 28-38 minutes per attempt. For Coder-Next, that money is wasted (0/10 ship). For 27B variants, ~70-80% of attempts ship.

### Cost-of-failure premium (p95 wall)

p95 wall reveals what pathological runs cost. The standout numbers:

| Cell | Model | Median wall | p95 wall | Failure mechanism on p95 |
|---|---|---|---|---|
| p3_business | 27B-no-think | 171 s | **3155 s** (53 min) | wall_killed_identical_call_loop ran 500 iters before harness gave up |
| p3_doc      | 27B-no-think | 144 s | **2971 s** (50 min) | same |
| p3_doc      | 27B (thinking) | 1113 s | **7976 s** (133 min) | identical-call-loop on word-trim, even longer |
| p2_hallucination | Coder-Next | 422 s | **1660 s** (28 min) | stuck_no_workspace_change_for_500_iters |

The 27B-thinking p95 of 7976 s ($0.144) for `p3_doc` is the single most expensive failure mode in this dataset.

### Expected cost per shipped run (the decision number)

For the 4 N=10 differential cells, total spend ÷ shipped runs gives the *true* cost of getting a usable artifact:

| Cell | Coder-Next | 27B (thinking) | 27B (no-think) |
|---|---:|---:|---:|
| p2_hallucination | 5/10 ships @ $0.0318/ship | 7/10 @ $0.0045 | 10/10 **@ $0.0023** |
| p3_business      | 10/10 **@ $0.0006**         | 9/9 @ $0.0039  | 8/10 @ $0.0536 |
| p3_doc           | 10/10 **@ $0.0007**         | 6/8 @ $0.0712  | 8/10 @ $0.0495 |
| p3_market        | 0/10 @ ∞                | 8/10 @ $0.0459 | 7/8 **@ $0.0493** |

**Headline: the cheapest-per-shipped-run model is task-class-specific.**
- For `p2_hallucination`, **27B-no-think is 14× cheaper per ship than Coder-Next** (which stucks half the time at full per-attempt cost).
- For `p3_business` and `p3_doc`, **Coder-Next is 60-100× cheaper per ship** than either 27B variant — when it ships, it ships fast.
- For `p3_market`, Coder-Next is unusable at any cost (∞ per ship); 27B variants are roughly tied at ~$0.05 per ship.

The "Coder-Next 4-12× cheaper" headline from `microbench-2026-04-28` survives at N=10 — but only on the cells where Coder-Next ships. On adversarial-hallucination, the equation flips.

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

### Operator-monitoring ROI on this chain

Concrete numbers from the runs caught by [`tooling/scripts/check_substance.py`](../../tooling/scripts/check_substance.py) during the final ~3 hours of the no-think chain:

- `p3_market_27b-nothink_v1` SIGTERM'd at iter 228 with no-progress = 205 / 500. Without intervention, the harness would have run another ~272 iters at ~30 s/iter ≈ **135 min GPU-time saved**.
- `p3_market_27b-nothink_v8` SIGTERM'd at iter 116 with no-progress ≈ 67 / 500. ~430 iters at ~30 s/iter ≈ **215 min GPU-time saved**.
- 4 `wall_killed_identical_call_loop` runs in `p3_business` and `p3_doc` ran to the harness's own 500-iter threshold (the substance-check workflow wasn't yet documented when those ran). With the workflow in place, they would have been SIGTERM'd at ~iter 30 of the streak.

**Aggregate savings on this chain**: roughly **5.8 GPU-hours** wall-time saved on the 2 caught scroll-loops alone. Projected savings if the workflow had been applied to all stuck-detector-eligible runs across the full no-think + Phase B chain (4 wall_killed in no-think + 2 SIGTERM'd + 5 wall_killed in 27B-thinking): ~10-14 GPU-hours / chain pass. At Tower2's 500 W cap and $0.13/kWh residential rate, that's roughly $0.65-0.91 in electricity — but the schedule benefit (cells unblock for the next run sooner) is the larger operational win on multi-day chains.

For new operators: this is the why-bother-running-substance-check number. The workflow is ~10 lines of cron, costs negligible CPU, and recovers GPU-hours per chain. See [`tooling/scripts/SUBSTANCE-MONITORING-WORKFLOW.md`](../../tooling/scripts/SUBSTANCE-MONITORING-WORKFLOW.md).

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

## How this drop relates to prior MMBT entries

### Strengthens claims from `microbench-2026-04-28`

| Prior claim (N=3 hint) | What this drop adds | Status |
|---|---|---|
| "27B is reliable at tight-schema tasks" — Phase 2 12/12 PASS | 27B-no-think 70/70 on P1+P2 at N=10 | **Strengthened** — no longer a small-N hint, bounded with Wilson [83.7%, 100%]. |
| "27B drives internet-research workflows that Coder-Next doesn't" — `p3_market` 27B 3/3 vs Coder 0/3 | Coder 0/10 at N=10 (Wilson 95% [0%, 27.8%]); 27B-thinking 8/10; 27B-no-think 7/10 | **Strengthened** — Coder collapse confirmed reproducible. 27B-no-think also drives this workflow, with caveat: scroll-loop pathology requires operator monitoring to keep wall time bounded. |
| "Coder-Next has a real hallucination-resistance gap" — 1/3 PASS on `p2_hallucination`, 2 confirmed-fabrications-as-real | Coder 5/10 stuck at N=10 (Wilson 95% [23.7%, 76.3%]); 27B-thinking 7/10; 27B-no-think 10/10 | **Strengthened + extended** — gap is now bounded as ~50% stuck rate. 27B-no-think (10/10) is the cleanest of the three on this cell. |
| "27B has a documented word-limit-trim failure mode" — `p3_doc` 0/3 PASS, 2 of 3 stuck in identical-call-loops | 27B-thinking 4/10 wall_killed at N=10 (Wilson [16.8%, 68.7%]); 27B-no-think 2/10 wall_killed | **Strengthened + partially mitigated** — bounded as a stable ~40% failure shape for thinking-mode; **disabling thinking drops it to ~20%**. |
| "Both miss multi-week risks on PM-synthesis" | 27B-no-think 10/10 ship on `p3_pm`, but PASS rate (risk recall) not yet re-graded | **Holds at ship-rate level**; PASS-rate re-grading pending. |

### Relates to `dreamserver-1-pr-audit` and `dreamserver-75-pr-audit`

The dreamserver PR audits are multi-hour research/audit tasks at much larger scope than the 5-30 minute microbench. Findings from those runs ("27B's analysis is high-quality but verdicts under-deliver"; "Coder-Next produces zero deliverable on the 75-PR audit") are about a **different operating regime** than this entry's data covers.

- **27B-no-think on long-form audits is untested** in this entry. The substance-monitoring methodology proven here (digit-stripped templates + tail-streak SIGTERM) could be applied to a future dreamserver-scale 27B-no-think run, and the no-think mode's word-budget improvements on `p3_doc` *suggest* it might also help with the verdict.md production issue 27B-thinking had on the dreamserver audits — but that's a hypothesis, not a finding.
- **Coder-Next's `p3_market` 0/10 collapse is consistent with its dreamserver-75-pr-audit failure** — both involve long-running research-shaped workflows where the model can't converge on a structured deliverable. The failure modes match: `stuck_no_workspace_change`, `identical-call-loop`, `cyclic-name-slop` (per the dreamserver entry), and `api_error: HTTP Error 400` (this entry).

The microbench gives bounded statistical evidence on 5-30 minute tasks. The dreamserver audits give existence proofs at multi-hour scope. They're complementary; neither generalizes to the other without explicit re-testing.

### Relates to `wallstreet-intern-test`

The wallstreet investment-memo task (N=3 per model on the original entry) showed 27B 1/3 ships and Coder-Next 1/3 ships, with both arms producing structurally complete memo repos when they shipped. The Phase B + no-think data doesn't include the wallstreet task class. **27B-no-think on wallstreet is untested.** Given the no-think mode's clean shipping on the microbench's `p3_business` (8/10) and `p3_doc` (8/10), there's reason to expect it would also handle a wallstreet-shaped multi-section memo cleanly — but again, hypothesis only.

## Recommended follow-ups

> Maintained list — see [`ROADMAP.md`](../../ROADMAP.md) for the consolidated cross-doc view with prioritization and contributor-welcome flags.

1. **PASS-rate grader sweep** on the no-think tarballs — promotes ship-rate findings to PASS-rate. Pending.
2. **Re-run N=3 P1 cells for 27B-thinking on the current harness** — definitively settle whether the 1/9 P1 ship rate is harness-drift or real model regression.
3. **Pairwise quality study extension** — add 27B-no-think as a third arm to the existing `pairwise-quality-study.md`. (Partially addressed by [`findings-pairwise-quality-three-model.md`](findings-pairwise-quality-three-model.md) on the 3 both-ship cells; the 4 differential cells are still open.)
4. **FP8 re-run of the same 12-cell grid.** Highest-priority external validation. Multiple field reports (see [`KNOWN-LIMITATIONS.md` § Cyankiwi 4-bit AWQ field reports](../../KNOWN-LIMITATIONS.md#quantization-specificity)) suggest the Cyankiwi 4-bit AWQ underperforms official FP8 / Unsloth UD4 of the same base models. Re-running on FP8 would let the ship-rate findings either generalize across quants or be bounded as quant-specific. Contributor-welcome via [`tooling/ADDING-A-MODEL.md`](../../tooling/ADDING-A-MODEL.md).
5. **M-series Mac sibling study.** The dense-vs-MoE compute tradeoff inverts on unified memory — Coder-Next (3B-active) wins on tokens-per-second; 27B (full-dense compute) becomes the bottleneck. Harness is portable; only the vLLM launch swaps for MLX. Contributor-welcome.
6. **Language-mix expansion for Phase 1.** Current Phase 1 cells (`p1_bugfix`, `p1_refactor`, `p1_testwrite`) all use a Python project (`logalyzer`). Adding C, JavaScript, or systems-programming starters would test whether Coder-Next's specialization manifests differently outside Python. Task-design work, not just a re-run.

## Caveats

- **Ship rate ≠ PASS rate.** This document reports `done_signal` rate. PASS rate analysis pending.
- **Harness drift across batches.** N=3 baselines used file_sha256 `7698067...`; the no-think grid used `7ea9592...`. The 4 N=10 differential cells share a single harness across all three model arms (consistent comparison). Cross-batch P1 numbers may include harness-related effects.
- **Operator-SIGTERM'd runs (2 of 27B-no-think `p3_market`)** are labeled `scroll-loop` in their `label.json` files (in the source bench's `submit/phase-b-overnight-2026-05-02` branch). They're counted as failures in this doc's denominators (hence 7/10 not 7/8 for the headline `p3_market` rate). Their transcripts are preserved; their `summary.json` and `workspace_final.tar.gz` are absent because operator-SIGTERM bypasses the harness teardown.
- **Wilson 95% CI** is conservative for small N; on the N=3 cells, CIs are wide and not reported here.
- **Phase B make-up turbulence** (the 27B-thinking arm specifically). The chain orchestrator's "end-of-night phase" detected three `api_error` failures in the original Phase B 27B-thinking runs (`p3_market_27b_v5/v6/v9`) and cleaned them for retry by deleting their `summary.json` + `workspace_final.tar.gz`. The retry loop ran v5 to clean `done_signal` (this is the published v5 data); v6 and v9 retries were stopped before completion and their original `api_error: timed out` (v6) / `api_error: HTTP Error 400: Bad Request` (v9) data was restored from the pre-makeup commit (`aba8a52` on the source bench's submit branch). The three runs in the published 27B-thinking `p3_market` data therefore reflect: v5 = retry (success), v6 / v9 = original (failure). The 27B-thinking p3_market 8/10 ship rate counts the v5 retry as a ship; if you want the pre-retry baseline rate, deduct one from that numerator.
