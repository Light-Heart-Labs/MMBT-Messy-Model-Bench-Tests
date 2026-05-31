# Qwen3.5-397B-A17B (GGUF, llama.cpp) — microbench N=10, vs Step-3.7-Flash + 27B/Coder-Next (Q4)

**N=10** (ten replicates per cell, both arms; 240 cells, all `done_signal`). Pair this with
[QUALITATIVE.md](QUALITATIVE.md): the pass/fail table below ties across a ~15× parameter range, and
the differences that matter are qualitative. Phase-1 cells graded with the **fixed** `phase1_grade.py`.

**Cross-model note:** the 27B / Coder-Next reference columns are the **Q4/AWQ** runs from
`benchmarks/microbench-2026-04-28` (N=1, clean `done_signal`, older agent-pilot harness). We attempted
fresh **Q8/FP8** runs of Qwen3.6-27B and Qwen3.6-35B-A3B on the current harness but **both were serving
failures** (35B: 36/36 HTTP-400; 27B-Q8: 23/36 token-runaway + 8/36 HTTP-400, only 4 clean) — **excluded,
not shown.** The Q4 artifacts are the trustworthy 27B/Coder comparison.

## Setup
- **Model:** Qwen3.5-397B-A17B, unsloth UD-Q3_K_XL GGUF (~167 GB on disk, 5 shards).
- **Engine:** llama.cpp `ghcr.io/ggml-org/llama.cpp:server-cuda-b9014`, pipeline parallel (`-sm layer`),
  `-ngl 999 -fa on -c 131072 -b 2048 -np 1 --jinja --reasoning-format none`, 2× RTX PRO 6000 Blackwell.
- **Two arms:** `enable_thinking` off (no-think) and on (think), via the harness `--thinking {on,off}`
  flag (sends `chat_template_kwargs.enable_thinking`).
- **Comparison:** Step-3.7-Flash-NVFP4 (vLLM, native CUTLASS FP4) low/med/high — see
  `../step3.7-flash-nvfp4-dual-blackwell-2026-05-28/`. Cross-engine + cross-quant: **"best-as-each-ships,"
  not a clean precision study.**

## Scorecard (N=10 for 397B; Step N=1/level; 27B+Coder Q4 N=1)

| task | 397B no-think | 397B think | Step low/med/high | 27B-Q4 (ref) | Coder-Q4 (ref) |
|---|:--:|:--:|:--:|:--:|:--:|
| p1_bugfix | 10/10 | 10/10 | ✓/✓/✓ | ‡ | ‡ |
| p1_testwrite † | 0/10 | 0/10 | ✗/✗/✗ | ‡ | ‡ |
| p1_refactor † | 0/10 | 0/10 | ✓/✗/✗ | ‡ | ‡ |
| p2_extract | 10/10 | 10/10 | ✓/✓/✓ | 3/3 | 3/3 |
| p2_ci | 10/10 | 10/10 | ✓/✓/✓ | 3/3 | 3/3 |
| p2_hallucination | 10/10 | 10/10 | ✓/✓/✓ | 3/3 | 1/3 |
| p2_triage | 10/10 | 10/10 | ~/✓/✓ | 3/3 | 3/3 |
| p3_doc | 9/10 | **2/10** | ~/✓/✓ | 0/3 | 2/3 |
| p3_business | 10/10 | 10/10 | ✓/~/✗ | 2/3 | 3/3 |
| p3_market * | **8/10** | **10/10** | ✗/✓/✓ | 3/3 * | 0/3 |
| p3_writing | 0/10 | 0/10 | ✗/~/✗ | 0/3 | 2/3 |
| p3_pm | **5/10** | **0/10** | ✗/~/✓ | 0/3 | 1/3 |
| **Total** | **82/120 (≈8.2/12)** | **72/120 (≈6/12)** | **7 / 8 / 8** | ~7/12 | ~7/12 |

† `p1_refactor` fails on structure (no `output/` subpackage created), not core-edit competence.
`p1_testwrite` — see grading-correctness note; the earlier "task-design" framing was partly a grader
artifact. \* `p3_market` is STRUCTURAL_PASS (citation validity is hand-graded).
**‡ QUARANTINED — 27B/Coder phase-1 (p1_*) reference cells are withheld pending [issue #29].** They were
graded by the same flat-vs-nested `phase1_grade.py` bug fixed in this entry, so the original published
values are self-flagged as untrustworthy (p1_testwrite especially is likely a guaranteed-FAIL artifact).
Their **p2/p3 cells are unaffected** by that bug and stay (used in the cross-model section below). The
397B/Step p1 cells use the *fixed* grader and are valid. Step N=1/level, 27B/Coder Q4 N=1 (p2/p3 only) —
directional; only 397B is N=10. Full per-replicate stability table + finish-reason audit in
[findings-n10.md](findings-n10.md).

### Grading-correctness fix (post-review, 2026-05-29)
A review caught that `phase1_grade.py` read flat keys (`coverage_pct`, `ruff_issues`, `benchmark_s`) while
`code_task_grader.py` writes nested ones (`coverage.line_coverage_pct`, `ruff.issue_count`,
`benchmark.elapsed_s`). Effect: `p1_bugfix`'s ruff/benchmark gates were silently always-true, and
`p1_testwrite`'s coverage gate was always-false. Fixed and **all phase-1 cells regraded** (N=1 and N=3):
- `p1_bugfix` PASS is genuinely validated: ruff 2→0 and benchmark **11.2s→0.537s** (the planted O(n²)
  fix) are real and pass — they were previously ignored. Consistent 3/3 both arms.
- `p1_testwrite` still FAILs, but the **reason flips**: think-mode actually achieved **99% coverage / 153
  passing tests** (the broken grader reported `cov=0` and hid it); it fails only on `logalyzer_unchanged`
  (it edited production code, violating the "only /tests/ may differ" rule). The model is *capable* here —
  the task constraint, not incapacity, is what fails it. The inherited † "task-design" footnote on testwrite
  is misleading and should be re-examined for the published 27B/Coder cells too.
- ⚠️ **The 27B / Coder reference columns predate this fix.** Their phase-1 (bug-fixing / test-writing)
  numbers came from the same buggy grader, so they may be wrong — testwrite especially is likely a
  guaranteed-FAIL artifact. **Historical phase-1 scores may need regrading; see tracking issue #29.**
  Treat the reference columns' p1_* cells as provisional until that lands.

## Headline findings

> **Lede (the two results that survive scrutiny):** this entry is **methodological, not "which model won."** Its two strongest, hardest-to-dismiss findings are (1) small-N misreads cells — a verdict that flips from fail→pass as N grows — and (2) on constraint-bound synthesis, *thinking actively hurts*, cross-validated across a 15× parameter range via the same mechanism. The "scale ties the aggregate" observation (now #3) is real but weaker — it leans on N=1 comparators and a cross-quant axis, so read it as suggestive, not a clean scaling law.

1. **Small-N misreads cells — demonstrated, not asserted.** This is the differentiated contribution. The
   auto-generated stability table ([findings-n10.md](findings-n10.md)) flags `p3_market` no-think as a
   **majority-verdict flip**: 1/3 at N=3 (reads as a *fail*) → **8/10** at N=10 (clearly a *pass*).
   `p3_pm` drifted 2/3 → 5/10 (a genuine coin-flip), `p3_doc` 9/10. Zero-variance cells (10/10 or 0/10):
   p1_bugfix, the grounded mid-tier (p2_extract/ci/hallucination/triage), p3_business, and the consistent
   fails. **The open-ended cells (market/pm/doc) are where single-N reads are unsafe — and they're exactly
   the cells everything else hinges on.** Caveat we hold ourselves to: see "Statistical honesty" below —
   the high-variance cells have wide Wilson intervals, so per-cell deltas are suggestive, not tight.

2. **Thinking is net-negative on constraint-bound synthesis, cross-validated across ~15× of scale.** For
   397B, thinking goes 82→72 (−10): it **helps exactly one task** — `p3_market` (8/10 → **10/10**) — and
   **hurts two**: `p3_doc` (9/10 → **2/10**) and `p3_pm` (5/10 → **0/10**). The `p3_doc` loss is mechanistic
   and *reproduces on the 27B-Q4* (N=10): a draft→count-words→over-limit→edit→recount loop. 397B trips the
   grader's 700-word limit; 27B-thinking literally `wall_killed`s in the loop ~40% of the time, which
   no-think halves — and 27B's overall ship rate is **86.8% no-think vs 75% thinking**. Same mechanism,
   opposite ends of the size range. **Reasoning is not a free upgrade; on constraint-bound synthesis it
   backfires regardless of model size.** (Honest scope: "net −10" is carried by two cells, doc −7 + pm −5
   — see "Statistical honesty.")

3. **Aggregate ties across the lineup — but read it as suggestive, with two confounds.** 397B (82/120,
   72/120), Step-3.7-Flash, Qwen3.6-27B-Q4, and Coder-Next-Q4 all land in the same ~7–8/12 band by per-task
   majority. **Two reasons not to over-read this as "scale doesn't matter":** (a) **cross-quant** — this is
   397B at *aggressive Q3_K_XL* (llama.cpp) vs an ~11B-active model at *NVFP4* (vLLM); it's
   "scale-at-3-bit vs small-at-4-bit," not a clean scale axis; (b) **N-asymmetry** — only 397B is N=10;
   Step is N=1/level and 27B/Coder are N=1, and this very entry proves N=1 misreads the open-ended cells.
   "Turn thinking on" is therefore a per-task decision, not a default — but "scale ties" itself is the
   most caveated claim here, not the headline.

4. **397B is runaway-resistant; its pathology is *stalling*.** Across all 240 N=10 cells, **zero
   max_tokens/length runaways** (the failure mode Flash showed on market at low effort, and that 27B-Q8
   showed 23/36 times). 397B's only non-clean exits are *stalls* (stuck-loop / model_stopped), and
   thinking specifically clears the no-think market stall. Failure *temperament* tracks training lineage,
   not size: 397B + 27B(-AWQ) stall, while Coder-Next + Flash run away (see QUALITATIVE.md).

5. **Cost still favors the small models.** 397B reaches the shared band at ~71 tok/s spanning both GPUs
   at Q3; Flash ~99 tok/s on one engine; 27B/Coder-Q4 far cheaper still. 397B earns its keep only where
   runaway-resistance + (thinking-on) market reliability justify the cost.

6. **Integration tax (a "messy model" finding).** Flash (vLLM) ran the harness out of the box. 397B
   (llama.cpp) needed `--reasoning-format none` (default extracts CoT into `reasoning_content`, leaving
   `content` empty → agent loop reads a thinking turn as "done" and dies at iter ~3 — invisible to a
   thinking-off smoke) plus harness cleanup fixes (non-sudo `rm` on root-owned sandbox/grader leftovers).
   All fixed in `tooling/`; see commit history.

See [QUALITATIVE.md](QUALITATIVE.md) for the behavioral analysis (token economy, packaging style,
failure-mode texture, reasoning shape) with per-cell citations.

## Statistical honesty — how tight is "net −10"?

The thinking-net-negative result rests on **two cells**, and at N=10 the per-cell verdicts have wide
Wilson 95% intervals. Stated plainly so it isn't over-read:

| cell | no-think | think | no-think Wilson 95% | think Wilson 95% | delta real? |
|---|:--:|:--:|:--:|:--:|:--:|
| p3_doc | 9/10 | 2/10 | [60%, 98%] | [6%, 51%] | **yes — CIs disjoint** |
| p3_pm | 5/10 | 0/10 | [24%, 76%] | [0%, 28%] | borderline — CIs nearly touch |
| p3_market | 8/10 | 10/10 | [49%, 94%] | [72%, 100%] | no — within noise |

So the honest version of headline #2: the **`p3_doc` think-hurts effect is statistically clean** (disjoint
intervals) *and* mechanistically explained (the word-limit loop, reproduced on 27B-Q4) — that's the load-
bearing result. `p3_pm` is suggestive but not significant at N=10; `p3_market`'s +2 is noise. "Net −10"
is directionally solid but driven by doc; don't quote it as a precise magnitude. The cross-model
reproduction (same loop on 27B) is what makes the *direction* trustworthy, not the single-model delta.

## Power behavior — are both GPUs ever near full power? No.

Captured live with `tooling/gpu_power_logger.sh` (5s cadence, cell-tagged) over the 397B N=10 run;
analyzed with `tooling/bench_power.py`. 3,868 paired samples.

| GPU | mean | p50 | p90 | max | % of 600W cap |
|---|--:|--:|--:|--:|--:|
| GPU0 | 307W | 346 | 366 | **539** | 90% |
| GPU1 | 279W | 324 | 335 | **475** | 79% |

- **Combined both-GPU draw: median 670W (56% of the 1200W cap), max 985W (82%). 0 of 3,868 samples came
  within 5% of full (1140W).** The pair never approaches the ceiling together.
- **Draw by phase:** decode bursts (util>20%) average 339W/GPU; CPU-bound tool phases (the `bench.py` /
  pytest calls in p1 cells, util<5%) drop to ~125W/GPU — a single GPU briefly nears its own 600W cap
  during sustained decode, but most wall-clock is spent well below it.
- **GPU0 leads GPU1 (+27W mean)** — the pipeline-parallel (`-sm layer`) signature: layers are split across
  the cards and fire in sequence, so the two rarely peak simultaneously. Combined with the CPU-bound tool
  phases, this is *why* the rig never thermally stresses on this workload.
- **Why it matters:** the "both GPUs at 600W = 1200W" worst case simply does not occur for single-stream
  agentic inference under pipeline parallelism. (Contrast confirmed by the MiniMax-M2.7 run, which uses
  vLLM **tensor**-parallel: both GPUs fire per token, combined active-decode draw **median ~896W, peak
  1089W (91% of cap), both GPUs >400W in 64% of samples, crossing 1000W** — the heaviest simultaneous
  draw of the bench. TP-vs-pipeline topology, not model size, drives it. See
  [findings-minimax-m2.7.md](findings-minimax-m2.7.md).)

## MiniMax-M2.7-NVFP4 (added — N=5, vLLM TP=2) — see [findings-minimax-m2.7.md](findings-minimax-m2.7.md)

Two findings, full detail in the linked doc:
1. **A temperature serving-trap, not a capability gap.** At the bench's default `temp=0.3`, MiniMax-NVFP4
   runs the agent loop correctly then degenerates into a repetition loop on its final turn
   (`model_exceeded_max_tokens`): **14/19 coding cells ran away (testwrite 10/10)**. At the model card's
   `temp=1.0/top_p=0.95/top_k=40`, the *same cells on the same 131072 cap* are **0/10 runaway**; all 60
   N=5 cells: **58 `done_signal`, 0 runaway**. Clean A/B → sampling, not the model, not the cap.
2. **An "exhaustive completer" temperament.** Aggregate **7/12 (35/60 cells)** — ties the ~7–8/12 band —
   but the shape is distinctive and **complementary to 397B**: **p2 analysis a perfect 20/20** (thoroughness
   pure upside), **scope-constrained coding 0/5 on both testwrite & refactor** (it edits files it was told
   to leave alone — real over-reach, opposite of 397B's surgical restraint), `p3_market` exhausts context
   (2× HTTP 400). *Deviation footnote: MiniMax alone runs temp=1.0 (off the temp=0.3 cohort) — justified
   because temp=0.3 is off-spec for it; and N=5 vs the cohort's N=10/N=1.*

## Cross-model qualitative (vs 27B / Coder-Next at Q4)

The aggregate ties, but the four models differ sharply in *behavior* — and the cleanest cut is **failure
temperament tracks training lineage, not parameter count**:

- **Token economy:** 27B-Q4 is the "honest middle" — more tokens than Coder-Next on grounded tasks, far
  fewer than 397B's scaffolding (397B over-documents with ADRs + navigation READMEs; Flash is terse;
  27B's done-summaries are the cleanest to actually read).
- **Failure signature:** **397B + 27B stall** (model_stopped / stuck-loop, never over-generate);
  **Coder-Next + Flash run away** (Coder hit the 180k cap on test-writing and a 502-iter stuck loop on
  market; Flash ran away on market at low effort). Two lineages, two temperaments — orthogonal to size.
- **The Q8 cautionary note:** fresh Qwen3.6-27B-**Q8** on the current harness ran away 23/36 times — a
  *serving-config* artifact, not the model (the Q4/AWQ 27B finishes clean). Quantization/serving choices
  can manufacture a failure mode that looks like model behavior; always check finish-reasons, not just
  pass/fail.

See [QUALITATIVE.md](QUALITATIVE.md) for the full per-cell behavioral analysis.

## Cross-model think-vs-no-think at N=10 (397B vs 27B-Q4, vs Coder-Next-Q4)

The 27B/Coder reference columns above are N=1 (`microbench-2026-04-28`). But we have a **richer Q4
dataset** that mirrors this study's exact design: `benchmarks/microbench-phase-b-2026-05-02` ran
**Qwen3.6-27B-AWQ at N=10 in BOTH thinking and no-think arms** (plus Coder-Next N=10) on the open-ended P3
differential cells. That lets us ask the *same* question of the 27B that we asked of the 397B — and the
answer rhymes.

**The headline: thinking is net-negative across a ~15× parameter range, via the same mechanism.**

| | thinking | no-think | Δ | shared mechanism |
|---|:--:|:--:|:--:|---|
| **397B** (N=10, pass) | 72/120 | **82/120** | **−10** | thinking craters `p3_doc` (9/10→2/10) on word-limit overrun |
| **27B-Q4** (N=10, ship on 4 differential cells) | 30/40 (75%) | **33/38 (86.8%)** | **+11.8pp for no-think** | thinking's `p3_doc` word-trim loop (4/10 `wall_killed`) drops to 2/10 without it |

Both models are **more reliable with thinking OFF**, and on both the **`p3_doc` synthesis task is where
thinking specifically hurts** — the model drafts, counts words, sees it's over the 700-word budget, edits,
recounts, and loops. 397B trips the *grader's* word limit (9→2 PASS); 27B-thinking literally `wall_killed`s
in the count-edit-recount loop ~40% of the time. Disabling thinking makes both "write once and ship."
**This is the strongest cross-scale result in the suite: reasoning is not a free upgrade — on
constraint-bound synthesis it actively backfires, independent of model size.**

### Per-cell ship-rate, P3 differential cells (all N=10, done_signal)

| cell | Coder-Next-Q4 | 27B-Q4 think | 27B-Q4 no-think | 397B no-think | 397B think |
|---|:--:|:--:|:--:|:--:|:--:|
| p2_hallucination | 10/10 | 7/10 | 5/10 (5 stuck) | 10/10 | 10/10 |
| p3_business | 10/10 | 9/10 | 8/10 | 10/10 | 10/10 |
| p3_doc | 10/10 | **6/10** | 8/10 | 9/10 | **2/10** |
| p3_market | **0/10** | 8/10 | 7/10 | 8/10 | 10/10 |
| p3_pm | 10/10 | 10/10 | 10/10 | 5/10 | 0/10 |

(27B/Coder = ship-rate `done_signal`; 397B = PASS — not perfectly identical metrics, but the shapes are
directly comparable. P1 coding cells excluded from the 27B cross-harness comparison: phase-b 27B-thinking
P1 used an older harness sha, so those aren't clean cross-harness — see that entry's caveats.)

### Failure temperament confirmed across the lineup (N=10, not anecdote)

- **Coder-Next runs away / fails hard:** `p3_market` **0/10** (reproducible STRUCTURAL_FAIL, Wilson 95%
  [0%, 27.8%]), `p2_hallucination` ~50% stuck. Bounded failure shapes, not flakes.
- **27B stalls in loops:** the word-trim `wall_killed_identical_call_loop` (write⇄word-count), plus
  `p3_market` scroll-loops (155-iter HTML-slice walks) — *stalling*, not over-generation.
- **397B stalls too** (stuck-loop / model_stopped, zero max_tokens runaways) — same temperament as 27B.
- **Flash runs away** (market at low effort) — same temperament as Coder-Next.

So **failure temperament clusters by training lineage, not parameter count**: the two Qwen-derived models
(397B, 27B) stall; the two others (Coder-Next, Flash) run away. A 15× size gap doesn't change the
temperament; shared lineage does.
