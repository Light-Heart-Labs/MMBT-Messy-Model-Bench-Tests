# Qwen3.5-397B-A17B (GGUF, llama.cpp) — microbench N=3, vs Step-3.7-Flash

**N=3** (three replicates per cell). Pair this with [QUALITATIVE.md](QUALITATIVE.md): the pass/fail
table below ties across models, and the differences that matter are qualitative. Phase-1 cells are
graded with the **fixed** `phase1_grade.py` (see grading-correctness note below).

## Setup
- **Model:** Qwen3.5-397B-A17B, unsloth UD-Q3_K_XL GGUF (~167 GB on disk, 5 shards).
- **Engine:** llama.cpp `ghcr.io/ggml-org/llama.cpp:server-cuda-b9014`, pipeline parallel (`-sm layer`),
  `-ngl 999 -fa on -c 131072 -b 2048 -np 1 --jinja --reasoning-format none`, 2× RTX PRO 6000 Blackwell.
- **Two arms:** `enable_thinking` off (no-think) and on (think), via the harness `--thinking {on,off}`
  flag (sends `chat_template_kwargs.enable_thinking`).
- **Comparison:** Step-3.7-Flash-NVFP4 (vLLM, native CUTLASS FP4) low/med/high — see
  `../step3.7-flash-nvfp4-dual-blackwell-2026-05-28/`. Cross-engine + cross-quant: **"best-as-each-ships,"
  not a clean precision study.**

## Scorecard (N=3, pass count per cell)

| task | 397B no-think | 397B think | Step low/med/high | 27B (ref) | Coder (ref) |
|---|:--:|:--:|:--:|:--:|:--:|
| p1_bugfix | 3/3 | 3/3 | ✓/✓/✓ | 3/3 | 2/3 |
| p1_testwrite † | 0/3 | 0/3 | ✗/✗/✗ | 0/3 † | 0/3 † |
| p1_refactor † | 0/3 | 0/3 | ✓/✗/✗ | 0/3 † | 0/3 † |
| p2_extract | 3/3 | 3/3 | ✓/✓/✓ | 3/3 | 3/3 |
| p2_ci | 3/3 | 3/3 | ✓/✓/✓ | 3/3 | 3/3 |
| p2_hallucination | 3/3 | 3/3 | ✓/✓/✓ | 3/3 | 1/3 |
| p2_triage | 3/3 | 3/3 | ~/✓/✓ | 3/3 | 3/3 |
| p3_doc | 2/3 | **1/3** | ~/✓/✓ | 0/3 | 2/3 |
| p3_business | 3/3 | 3/3 | ✓/~/✗ | 2/3 | 3/3 |
| p3_market * | **1/3** | **3/3** | ✗/✓/✓ | 3/3 * | 0/3 |
| p3_writing | 0/3 | 0/3 | ✗/~/✗ | 0/3 | 2/3 |
| p3_pm | **2/3** | **0/3** | ✗/~/✓ | 0/3 | 1/3 |
| **Total** | **23/36** | **22/36** | **7 / 8 / 8** | ~7/12 | ~7/12 |

† `p1_refactor` fails on structure (no `output/` subpackage created), not the model's competence at the
core edit. `p1_testwrite` — see the grading-correctness note below; the earlier "task-design" framing was
partly a grader artifact. \* `p3_market` is graded STRUCTURAL_PASS (citation validity is a hand-grading dimension).

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

1. **Scale doesn't move the aggregate.** 397B lands at 23/36 (no-think) and 22/36 (think) — the *same
   7–8/12 band* (by per-task majority) as a 27B, a ~30B coder, and an ~11B-active Flash. The interesting
   signal is per-task and qualitative, not the total.

2. **Thinking is net −1 for 397B (8/12→7/12 at N=1, 23/36→22/36 at N=3) — but N=3 overturns the N=1
   "inert" reading.** At N=1 the loss looked like a single verbosity flip (`p3_doc`). With three
   replicates, thinking is not inert — it **redistributes**: it *helps* `p3_market` (no-think 1/3 → think
   **3/3**, stabilizing the wobbliest cell, zero runaways) but *hurts* `p3_pm` (2/3 → **0/3**) and `p3_doc`
   (2/3 → 1/3, the verbosity-vs-word-limit story). Net −1, but as a wash of real per-task swings, not a
   no-op. Reasoning changes *where* 397B succeeds without changing *how often*.

3. **N=3 exposes which N=1 verdicts were luck.** Single replicates are noisy on the open-ended cells: in
   the no-think arm, `p3_market` (N=1 ✓ → N=3 1/3) and `p3_pm` (N=1 ✗ → N=3 2/3) were single-draw
   artifacts; `p3_doc` (✓ → 2/3) wobbles on the word limit. Zero-variance cells (3/3 or 0/3 across all
   reps): p1_bugfix, the grounded mid-tier (p2_extract/ci/hallucination/triage), p3_business, and the
   consistent fails. **Trust the mid-tier and bugfix; treat market/pm/doc as high-variance.**

4. **397B is runaway-resistant; Flash is not (at low effort).** All 72 397B cells (both arms × N=3)
   finished `done_signal` — zero max_tokens/length failures, including `p3_market` think at 3/3.
   Step-3.7-Flash **ran away on `p3_market` at low effort** (hit max_tokens). 397B's reliability edge is
   real and mode-independent — and for market research specifically, thinking turns it from a coin-flip
   (1/3) into a lock (3/3).

5. **Cost still favors Flash.** 397B reaches the shared band at ~71 tok/s spanning both GPUs at Q3, vs
   Flash ~99 tok/s on one engine. Flash is the better default; 397B earns its keep where its runaway
   resistance + (thinking-on) market-research reliability matter.

6. **Integration tax (a "messy model" finding).** Flash (vLLM) ran the harness out of the box. 397B
   (llama.cpp) needed `--reasoning-format none` (default extracts CoT into `reasoning_content`, leaving
   `content` empty → agent loop reads a thinking turn as "done" and dies at iter ~3 — invisible to a
   thinking-off smoke) plus harness cleanup fixes (non-sudo `rm` on root-owned sandbox/grader leftovers).
   All fixed in `tooling/`; see commit history.

See [QUALITATIVE.md](QUALITATIVE.md) for the behavioral analysis (token economy, packaging style,
failure-mode texture, reasoning shape) with per-cell citations.
