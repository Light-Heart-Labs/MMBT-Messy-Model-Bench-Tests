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
| p1_bugfix | 10/10 | 10/10 | ✓/✓/✓ | 3/3 | 2/3 |
| p1_testwrite † | 0/10 | 0/10 | ✗/✗/✗ | 0/3 † | 0/3 † |
| p1_refactor † | 0/10 | 0/10 | ✓/✗/✗ | 0/3 † | 0/3 † |
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
artifact. \* `p3_market` is STRUCTURAL_PASS (citation validity is hand-graded). Step N=1/level, 27B/Coder
Q4 N=1 — directional; only 397B is N=10. Full per-replicate stability table + finish-reason audit in
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

1. **Scale doesn't move the aggregate — confirmed at N=10.** 397B lands at 82/120 (no-think) / 72/120
   (think) = the *same 7–8/12 band* (by per-task majority) as Step-3.7-Flash (~11B active), Qwen3.6-27B
   (Q4), and Qwen3-Coder-Next (Q4). A ~15× parameter spread barely moves aggregate pass-rate on this
   suite. The signal is per-task and qualitative, not the total.

2. **Thinking is net −10 at N=10 (82→72) — decisively negative, via concentrated redistribution.** N=3
   hinted at this (−1); N=10 makes it unambiguous. Thinking **helps exactly one task** — `p3_market`
   (no-think 8/10 → think **10/10**) — and **hurts two, hard**: `p3_doc` (9/10 → **2/10**, the
   verbosity-blows-the-word-limit effect) and `p3_pm` (5/10 → **0/10**, over-deliberation wrecks
   project-mgmt). Everywhere else identical. Reasoning changes *where* 397B succeeds, and on net makes it
   worse here — "turn thinking on" is a per-task decision, not a default.

3. **N=10 overturns small-N luck — quantified.** The auto-generated stability table
   ([findings-n10.md](findings-n10.md)) flags `p3_market` no-think as a **majority-verdict flip**: 1/3 at
   N=3 (looked like a fail) → **8/10** at N=10 (clearly a pass). `p3_pm` no-think drifted 2/3 → 5/10 (a
   true coin-flip), `p3_doc` 9/10 (occasional word-limit trip). Zero-variance cells (10/10 or 0/10):
   p1_bugfix, the grounded mid-tier (p2_extract/ci/hallucination/triage), p3_business, and the consistent
   fails. **Trust the mid-tier + bugfix; market/pm/doc are the high-variance cells — and small N misreads
   them.** This is the headline methodological result.

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
  agentic inference under pipeline parallelism. (The MiniMax-M2.7 run uses vLLM **tensor**-parallel, which
  fires both GPUs per token — the expected contrast is a higher, more simultaneous combined draw; that
  comparison is added when the MiniMax run lands.)

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
