# Microbench Index — the 12-family agentic microbench, across both trees

> **Why this file exists.** The MMBT "12-family agentic microbench" (the same harness, task families,
> think/no-think comparison, and `done_signal`/PASS scorecard) is a **model-behavior** study. Its entries
> are split across two top-level trees for an *accidental* reason — some models needed the dual-Blackwell
> rig (so they landed under `hardware-tests/`), the earlier 4-bit runs are under `benchmarks/`. This index
> gathers all of them in one place so you don't have to know which tree a model happened to land in.
>
> Each entry below is a 12-family microbench. The `hardware-tests/` ones also carry a secondary power
> section, but their *headline* is model behavior.

## All 12-family microbench entries

| Entry | Tree | Models / arms | N | Headline |
|---|---|---|---|---|
| [`microbench-2026-04-28`](benchmarks/microbench-2026-04-28/) | benchmarks/ | Qwen3.6-**27B-AWQ** vs Qwen3-Coder-Next-**AWQ** | 3 | Aggregate-tied ~7/12 each; complementary task-class strengths; Coder-Next much faster/cheaper. |
| [`microbench-phase-b-2026-05-02`](benchmarks/microbench-phase-b-2026-05-02/) | benchmarks/ | + **27B-AWQ no-think** third arm; 4 differential cells to N=10 | 10 | 27B ships 86.8% no-think vs 75% think (same `p3_doc` word-limit loop); Coder-Next market 0/10 (Wilson [0, 27.8%]). |
| [`qwen3.5-397b-vs-step3.7-flash-2026-05-29`](hardware-tests/qwen3.5-397b-vs-step3.7-flash-2026-05-29/) | hardware-tests/ | **397B-A17B** (Q3 GGUF) no-think/think; **Step-3.7-Flash** (NVFP4) low/med/high; **MiniMax-M2.7** (NVFP4); **27B-Q4 / Coder-Q4** refs | 10 / 1 / 5 | Thinking net-negative (397B 82→72); small-N misreads cells; aggregate ties ~7–8/12 across ~15× scale; MiniMax "exhaustive completer" + temp serving-trap. |
| [`qwen3.6-27b-fp8-microbench-2026-05-31`](hardware-tests/qwen3.6-27b-fp8-microbench-2026-05-31/) | hardware-tests/ | Qwen3.6-**27B-FP8** no-think/think | 5 | Thinking net-negative (35/60 vs 29/60); `p2_triage` 0/5 think vs 5/5 no-think; FP8 serving stable where Q8 failed. |

## The four "27B"s — don't conflate them

This study references Qwen3.6-27B in **four** different forms. When you see "27B," check which:

| Label | What it is | Where |
|---|---|---|
| **27B-AWQ** (= "27B-Q4") | Cyankiwi 4-bit AWQ, vLLM | `microbench-2026-04-28`, `microbench-phase-b-2026-05-02`; the "27B-Q4 ref" columns in the 397B entry; the AWQ rows in `SCORECARD.md` / `COMPARISON.md` |
| **27B-Q8** | Q8_0 GGUF, llama.cpp | `hardware-tests/qwen3.6-q8-fleet-2026-05-17` (throughput); attempted on the microbench harness but **excluded as a serving failure** (23/36 token-runaway) — see the 397B entry |
| **27B-FP8** | official FP8, vLLM | `hardware-tests/qwen3.6-27b-fp8-microbench-2026-05-31` (this is the clean redo of the excluded Q8/FP8 attempt) |
| **35B-A3B** (sibling MoE) | Qwen3.6-35B-A3B, various quants | referenced as the small-MoE comparator; Q8 MoE crashes on Blackwell sm_120 (known kernel bug) |

## The one finding that holds across all of them

**Thinking is net-negative on this agentic microbench**, consistently across a ~15× parameter range:
397B 82→72 (−10), 27B-AWQ 86.8%→75% ship rate, 27B-FP8 35→29 (−6) — all the same direction, largely via
the same `p3_doc` word-limit / over-production mechanism (see [issue #36](https://github.com/Light-Heart-Labs/MMBT-Messy-Model-Bench-Tests/issues/36)
for the grader artifact that compounds it). Failure *temperament* tracks lineage, not size: Qwen-family
models (397B, 27B) **stall**; Coder-Next / Flash / MiniMax(@temp0.3) **run away**.

## Note on organization

This index is the low-disruption fix for the cross-tree split (it avoids moving directories, which would
break links and git history). If the microbench corpus keeps growing, the cleaner long-term move is a
dedicated `microbenchmarks/` tree; this index is the bridge until then.
