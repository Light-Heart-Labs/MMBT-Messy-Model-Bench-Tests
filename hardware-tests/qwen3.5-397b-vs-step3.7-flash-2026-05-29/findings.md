# Qwen3.5-397B-A17B (GGUF, llama.cpp) — microbench N=1, vs Step-3.7-Flash

**Provisional / N=1.** One replicate per cell — directional, not statistically settled. An N=3
re-run is queued. Pair this with [QUALITATIVE.md](QUALITATIVE.md): the pass/fail table below ties
across models, and the differences that matter are qualitative.

## Setup
- **Model:** Qwen3.5-397B-A17B, unsloth UD-Q3_K_XL GGUF (~167 GB on disk, 5 shards).
- **Engine:** llama.cpp `ghcr.io/ggml-org/llama.cpp:server-cuda-b9014`, pipeline parallel (`-sm layer`),
  `-ngl 999 -fa on -c 131072 -b 2048 -np 1 --jinja --reasoning-format none`, 2× RTX PRO 6000 Blackwell.
- **Two arms:** `enable_thinking` off (no-think) and on (think), via the harness `--thinking {on,off}`
  flag (sends `chat_template_kwargs.enable_thinking`).
- **Comparison:** Step-3.7-Flash-NVFP4 (vLLM, native CUTLASS FP4) low/med/high — see
  `../step3.7-flash-nvfp4-dual-blackwell-2026-05-28/`. Cross-engine + cross-quant: **"best-as-each-ships,"
  not a clean precision study.**

## Scorecard (N=1)

| task | 397B no-think | 397B think | Step low/med/high | 27B (ref N=3) | Coder (ref N=3) |
|---|:--:|:--:|:--:|:--:|:--:|
| p1_bugfix | ✓ | ✓ | ✓/✓/✓ | 3/3 | 2/3 |
| p1_testwrite † | ✗ | ✗ | ✗/✗/✗ | 0/3 † | 0/3 † |
| p1_refactor † | ✗ | ✗ | ✓/✗/✗ | 0/3 † | 0/3 † |
| p2_extract | ✓ | ✓ | ✓/✓/✓ | 3/3 | 3/3 |
| p2_ci | ✓ | ✓ | ✓/✓/✓ | 3/3 | 3/3 |
| p2_hallucination | ✓ | ✓ | ✓/✓/✓ | 3/3 | 1/3 |
| p2_triage | ✓ | ✓ | ~/✓/✓ | 3/3 | 3/3 |
| p3_doc | ✓ | **✗** | ~/✓/✓ | 0/3 | 2/3 |
| p3_business | ✓ | ✓ | ✓/~/✗ | 2/3 | 3/3 |
| p3_market * | ✓ | ✓ | **✗**/✓/✓ | 3/3 * | 0/3 |
| p3_writing | ✗ | ✗ | ✗/~/✗ | 0/3 | 2/3 |
| p3_pm | ✗ | ✗ | ✗/~/✓ | 0/3 | 1/3 |
| **Total** | **8/12** | **7/12** | **7 / 8 / 8** | ~7/12 | ~7/12 |

† `p1_refactor` fails on structure (no `output/` subpackage created), not the model's competence at the
core edit. `p1_testwrite` — see the grading-correctness note below; the earlier "task-design" framing was
partly a grader artifact. \* `p3_market` is graded STRUCTURAL_PASS (citation validity is a hand-grading dimension).

### Grading-correctness fix (post-review, 2026-05-29)
A review caught that `phase1_grade.py` read flat keys (`coverage_pct`, `ruff_issues`, `benchmark_s`) while
`code_task_grader.py` writes nested ones (`coverage.line_coverage_pct`, `ruff.issue_count`,
`benchmark.elapsed_s`). Effect: `p1_bugfix`'s ruff/benchmark gates were silently always-true, and
`p1_testwrite`'s coverage gate was always-false. Fixed and **all phase-1 cells regraded**. Outcome:
- **Totals unchanged (8/12 / 7/12)** — but now *trustworthy*, not coincidental.
- `p1_bugfix` PASS is now genuinely validated: ruff 2→0 and benchmark **11.2s→0.537s** (the planted O(n²)
  fix) are real and pass — they were previously ignored.
- `p1_testwrite` still FAILs, but the **reason flips**: think-mode actually achieved **99% coverage / 153
  passing tests** (the broken grader reported `cov=0` and hid it); it fails only on `logalyzer_unchanged`
  (it edited production code, violating the "only /tests/ may differ" rule). The model is *capable* here —
  the task constraint, not incapacity, is what fails it. The inherited † "task-design" footnote on testwrite
  is misleading and should be re-examined for the published 27B/Coder cells too.

## Headline findings

1. **Scale doesn't move the aggregate.** A 397B-param model lands in the *same 7–8/12 band* as a 27B,
   a ~30B coder, and an ~11B-active Flash. The interesting signal is per-task and qualitative, not the total.

2. **Thinking is net −1 for 397B on this suite** (8/12 → 7/12). 11 of 12 cells are identical between modes;
   the lone flip is `p3_doc` PASS→FAIL — and it's instructive: *both* modes captured all 8/8 facts
   (`fact_coverage 1.0`); think just wrote 721 words against a 700-word limit (no-think: 692). Reasoning
   amplified 397B's verbosity and blew a hard constraint with identical content. Thinking was inert
   everywhere else — more tokens and turns, same outcomes. **Reasoning bought 397B nothing here.**

3. **397B is runaway-resistant; Flash is not (at low effort).** All 24 397B cells (both arms) finished
   `done_signal` — zero max_tokens/length failures. Step-3.7-Flash **ran away on `p3_market` at low effort**
   (hit max_tokens). 397B's reliability edge is real and mode-independent.

4. **397B's distinctive lane is long-form synthesis** (`p3_doc`/`p3_business`/`p3_market` all pass in
   no-think) where the 27B was weak — but it's the **slowest and most expensive** way to reach the shared
   band (~71 tok/s spanning both GPUs at Q3, vs Flash ~99 tok/s on one engine). Flash is the better default;
   397B earns its keep only where synthesis reliability and a single stable setting matter.

5. **Integration tax (a "messy model" finding).** Flash (vLLM) ran the harness out of the box. 397B
   (llama.cpp) needed `--reasoning-format none` (default extracts CoT into `reasoning_content`, leaving
   `content` empty → agent loop reads a thinking turn as "done" and dies at iter ~3 — invisible to a
   thinking-off smoke) plus harness cleanup fixes (non-sudo `rm` on root-owned sandbox/grader leftovers).
   All fixed in `tooling/`; see commit history.

See [QUALITATIVE.md](QUALITATIVE.md) for the behavioral analysis (token economy, packaging style,
failure-mode texture, reasoning shape) with per-cell citations.
