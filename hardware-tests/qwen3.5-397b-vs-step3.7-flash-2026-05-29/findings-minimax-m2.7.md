# MiniMax-M2.7-NVFP4 on 2× RTX PRO 6000 Blackwell — microbench N=5 (+ the temp serving-trap)

MiniMax-M2.7 (230B-A10B MoE), served as **NVFP4 on vLLM tensor-parallel (TP=2)**, run through the MMBT
12-family agentic microbench. Added to the [397B vs Step-3.7-Flash entry](findings.md) as a fifth model.

**N=5** per cell (60 cells). Comparators in the main entry are N=10 (397B) / N=1 (Step, 27B-Q4, Coder-Q4) —
so MiniMax is **N=5, an asymmetry to read with the same caution this entry already documents for small N.**

## TL;DR — two findings, the first is the bigger one

1. **A serving trap, not a capability gap (the headline).** Run at the bench's cross-model default
   **`temperature=0.3`**, MiniMax-NVFP4 looked *broken* on coding: it ran the agent loop correctly for
   ~29 iterations, then on the **final text turn entered a repetition loop that generated tens of
   thousands of tokens to the `max_tokens` cap** (`finish_reason: model_exceeded_max_tokens`). Across the
   two coding families the temp=0.3 run reached before it was stopped: **14/19 cells ran away (74%)** —
   `p1_bugfix` 4/9, `p1_testwrite` **10/10**. Re-run at MiniMax's **model-card sampling
   (`temperature=1.0, top_p=0.95, top_k=40`)**, the *same cells on the same 131072 cap* produce **0/10
   runaways** — clean `done_signal`. Across all **60** N=5 cells: **58 `done_signal`, 0 runaways**, 2
   context-exhaustion. The clean A/B on the identical cell/cap proves the runaway was **sampling**, not
   the model and not a stingy token cap. *Greedy-ish decode on a reasoning model is a documented
   repetition-loop trap; MiniMax's card mandates temp=1.0.*

2. **MiniMax is an "exhaustive completer" — a genuinely double-edged temperament.** Its instinct is to do
   the maximum: fix every bug it sees, write a full test suite + audit/ADR/CHANGELOG docs, research
   exhaustively. This **dominates open analysis** and **sinks scope-constrained edits** (see scorecard).
   It is the mirror image of 397B's surgical restraint.

## The serving trap — before/after on the same cells

| family | temp=0.3 (broken) | temp=1.0 (spec) |
|---|---|---|
| p1_bugfix | 5 `done_signal` / **4 runaway** (44%) | **5 `done_signal` / 0 runaway** |
| p1_testwrite | 0 / **10 runaway (100%)** | **5 `done_signal` / 0 runaway** |
| all 60 cells (spec) | — | **58 `done_signal`, 0 runaway, 2 ctx-exhaustion** |

A temp=0.3-runaway cell generated **58k–106k tokens in a single final turn** (the testwrite cells cluster
at 71k–106k; two bugfix cells dip to ~59k/75k). That is degenerate repetition, not legitimate output —
and the identically-capped 397B (also 131072, also temp 0.3-equivalent path) had **0 runaways in 260
cells**, so the cap is not the cause.

## Scorecard (N=5; PASS = grader verdict, majority ≥3/5 marks the family ✓)

| family | PASS/5 | avg iters | dominant fail-reason |
|---|---|---|---|
| p2_extract | **5/5** ✓ | 11 | — |
| p2_ci | **5/5** ✓ | 41 | — |
| p2_hallucination | **5/5** ✓ | 15 | — |
| p2_triage | **5/5** ✓ | 13 | — |
| p3_business | **5/5** ✓ | 18 | — |
| p3_doc | **4/5** ✓ | 19 | 1× word-limit |
| p3_pm | **3/5** ✓ | 14 | — |
| p1_bugfix | 2/5 | 131 | `ruff_no_regression` ×3 (lint nits in its own new tests) |
| p3_writing | 1/5 | 30 | length/quality |
| p1_testwrite | 0/5 | 86 | `logalyzer_unchanged` ×5 (**scope violation**) |
| p1_refactor | 0/5 | 75 | `tests_unchanged` ×5, `non_output_files_unchanged` ×2 (**scope violation**) |
| p3_market | 0/5 | 51 | 2× **ctx-exhaustion (HTTP 400)** + 3 fail |

**Aggregate: 7/12 families pass majority; 35/60 cells (58%).** This lands in the same **~7–8/12 band** as
397B (8/12 no-think), Step-3.7-Flash, 27B-Q4 and Coder-Q4 — MiniMax **aggregate-ties the field, but the
per-family *shape* is distinctive** (and that shape, not the tie, is the finding).

## Qualitative — the "exhaustive completer" pattern (every claim cited to graded cells)

- **Open analysis = pure upside. p2 is a perfect 20/20** (extract/ci/hallucination/triage all 5/5), fast
  (~11–41 iters). When there is no scope or length constraint, thoroughness only helps. Best-in-class here.
- **Scope-constrained coding = real liability, not a grader artifact. `p1_testwrite` 0/5 and `p1_refactor`
  0/5**, failing on **substantive** criteria: the test-writing task says *"add tests, leave the production
  code unchanged"* → MiniMax rewrites the production code anyway (`logalyzer_unchanged` fails 5/5); the
  refactor task says *"only touch the output package"* → it modifies tests and out-of-scope files
  (`tests_unchanged` 5/5, `non_output_files_unchanged` 2/5). It **cannot resist improving everything**,
  which is exactly what these guardrails forbid. This is the **opposite of 397B**, whose surgical restraint
  *passes* `p1_refactor`.
- **`p1_bugfix` is the in-between case (2/5):** it fixes the planted bugs correctly (the O(n²) `load()`
  measured 11.9s→0.57–0.63s by the grader; the `collections.Iterable` import removed; 69–82 tests pass)
  but trips `ruff_no_regression` (2→3, 2→5) on **unused-import nits in its own newly-written tests** —
  a lint technicality. *Here* the binary score understates it; on testwrite/refactor it does not.
- **Open-ended sinks exhaust context. `p3_market` 0/5**, with **2 cells hitting the 131072 ceiling
  outright (HTTP 400)** — it keeps issuing research tool-calls until the conversation won't fit. The p3
  analog of over-delivery.
- **Structured synthesis is fine** — `p3_business` 5/5, `p3_doc` 4/5, `p3_pm` 3/5. Where the deliverable
  is well-bounded, the thoroughness lands.
- **Failure texture is its own category:** not 397B's quiet *stall* (omission), not Coder/Flash's
  *runaway* (over-generation cutoff) — MiniMax's misses are **self-inflicted: scope violations and context
  exhaustion from doing too much.** And it is **expensive** — 75–131 iters/cell on p1 (the high end of the
  field) vs ~11–18 on the analysis cells it aces.

**One-line verdict:** complementary to 397B. MiniMax aces analysis where 397B is average; 397B respects
guardrails where MiniMax bulldozes them. A task-class strengths finding, not a scaling-law tie.

## GPU power — TP=2 loads both GPUs in balance (no quantified peak this run)

> **Data caveat (important):** continuous power sampling for the MiniMax run was **not reliably captured**
> — the per-sample logger output for this run is missing/untagged, so the active-decode median/peak
> percentiles are **not available**. An earlier draft of this doc cited specific figures
> (~896W median / 1089W peak / 64%-of-samples / "crosses 1000W"); those are **unverifiable against any
> committed data and are withdrawn.** The only surviving power data is the per-cell instantaneous
> `receipt.json` `nvidia-smi` snapshot (one sample per cell), which is **not** a decode-peak measurement.

What the **60 receipt snapshots** show (instantaneous, N=60 cells): combined draw **median 612W, max 703W**,
balanced per-GPU (**GPU0 ~313W / GPU1 ~300W median**), and **0/60 above 1000W**. These confirm TP=2's
*balance* — both GPUs draw nearly equally, the signature of tensor-parallel splitting each layer across
both cards — but because the snapshots are single instantaneous samples (likely caught outside sustained
decode), they **undersample peak draw and cannot be compared** to 397B's continuously-sampled pipeline
figures (median 670W / max 985W over 3,868 samples).

**The defensible claim is architectural, not a measured peak:** tensor-parallel makes both GPUs compute
each layer *simultaneously* (so they fire together), whereas pipeline-parallel *alternates* them (GPU0
leads, combined draw staggered). MiniMax's balanced per-GPU snapshots are consistent with that; a
quantified simultaneous-peak comparison to 397B would need a re-run with the per-sample logger fixed.

## Caveats (read these with the numbers)

- **Sampling deviation:** MiniMax ran at its **card-specified `temp=1.0/top_p=0.95/top_k=40`**, *not* the
  bench's cross-model `temp=0.3`. This is a deliberate, documented per-model deviation — at temp=0.3 the
  model is off-spec and degenerates (finding #1), so a temp=0.3 score would be meaningless. The receipt
  schema records `temperature` but **not** `top_p`/`top_k`; the full profile is recorded here and in the
  launch command.
- **N=5 vs comparators' N=10/N=1** — directional. The per-family rates above (esp. the 0/5 and 5/5 ones)
  are stable enough to characterize, but treat the aggregate as ±1 family.
- **131072 context** (vs Step/27B/Coder at 262144) — a real cap asymmetry, footnoted; it did not cause the
  runaways (those were sampling) but it is where `p3_market` exhausted context. MiniMax's native max is ~196k.
- **NVFP4 on Blackwell SM120** is a maturity-rough surface (vLLM has open repetition/kernel issues for
  MiniMax-NVFP4); we did **not** use `--enable-expert-parallel` (the named trigger in vLLM #31856).
- This build emits **no separate `<think>`/`reasoning_content`** despite MiniMax-M2 being an
  interleaved-thinking model — so the interleaved-thinking history requirement was moot here (the harness
  retains `reasoning_content` defensively regardless).

## Reproduce
```bash
# Serve (vLLM TP=2, NVFP4). minimax_m2 parsers; no expert-parallel.
docker run -d --name vllm-minimax --gpus all --shm-size 16g -e NCCL_P2P_DISABLE=1 \
  -v $HOME/models:/models:ro -p 127.0.0.1:8001:8000 vllm/vllm-openai:latest \
  --model /models/nvidia-MiniMax-M2.7-NVFP4 --served-model-name minimax-m2.7 \
  --tensor-parallel-size 2 --gpu-memory-utilization 0.92 --quantization modelopt \
  --trust-remote-code --max-model-len 131072 --disable-custom-all-reduce \
  --tool-call-parser minimax_m2 --reasoning-parser minimax_m2 --enable-auto-tool-choice \
  --host 0.0.0.0 --port 8000

# Run at the model card's sampling (BENCH_* env overrides the default temp=0.3):
BENCH_TEMP=1.0 BENCH_TOP_P=0.95 BENCH_TOP_K=40 \
  bash tooling/scripts/run_microbench.sh minimax-m2.7 8001 minimax-m2.7-spec 5 "" "" 131072
bash tooling/scripts/grade_microbench.sh minimax-m2.7-spec
```
