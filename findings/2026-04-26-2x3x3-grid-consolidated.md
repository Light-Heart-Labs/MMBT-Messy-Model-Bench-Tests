# 2026-04-26 — Consolidated 2×3×3 grid (2 tasks × 3 models × 3 runs)

> Two task types (investment memo, board presentation), three models (27B-AWQ dense, Coder-Next-AWQ MoE, 35B-A3B-AWQ MoE), three runs each at `temperature=0`. **18 runs total.** Headline: the task matters far more than the model. Board task succeeds 67% of the time across all models; memo task only 22%.

## Setup invariants

- vLLM image: `vllm/vllm-openai:latest` (`sha256:2622f38a…`) for all 18 runs
- All runs at `temperature=0`, no system prompt, task prompt verbatim
- Per-run sandbox container, fresh git workspace per run
- Same harness across the batch (with three mid-batch fixes — see HARNESS-CHANGELOG.md):
  - `--input-mount` flag added before board-task runs
  - `seed: 42` per-request (added during determinism investigation, kept for batch)
  - Tool-args truncation bumped 2KB→50KB so transcripts capture model behavior
- Board task input: `agent-pilot/inputs/27b-awq-gtlb-memo/` (extracted from 27B's canonical memo run, .git intact)

## Outcome grid

### Success rate by (model × task)

| | **Memo** | **Board** | row total |
|---|:---:|:---:|:---:|
| **27B-AWQ** | 1/3 | 2/3 | 3/6 |
| **Coder-Next-AWQ** | 1/3 | **3/3** | 4/6 |
| **35B-A3B-AWQ** | 0/3 | 1/3 | 1/6 |
| **column total** | **2/9 (22%)** | **6/9 (67%)** | 8/18 (44%) |

Where "success" = `finish_reason: done_signal` AND a real deliverable produced (memo with content / pptx + audit trail). Partial successes (model_stopped with substantive work) count as ½ in the eyeball score below but not in this binary.

### Run-by-run detail

**Investment memo task** (rough scores):

| run | iters | wall | finish | rough |
|---|---:|---:|---|---:|
| 27b memo v2 | 56 | 28 min | done_signal ⭐ | **85** |
| 27b memo v3 | 40 | 11.5 min | model_stopped (parser fault) | 50 |
| 27b memo v4 | 45 | 68 min | api_error: timed out | 10 |
| coder memo v5 | 95 | 11 min | done_signal ⭐ | **80** |
| coder memo v6 | 37 | 2 min | stuck | 5 |
| coder memo v7 | 63 | 2 min | stuck | 10 |
| 35ba3b memo v1 | 51 | 6 min | stuck | 10 |
| 35ba3b memo v2 | 14 | 0.2 min | model_stopped | 3 |
| 35ba3b memo v3 | 38 | 7 min | exceeded_max_tokens_64000 | 5 |

**Board presentation task** (rough scores):

| run | iters | wall | finish | rough |
|---|---:|---:|---|---:|
| 27b board v1 | 66 | 34 min | done_signal ⭐ | **92** |
| 27b board v2 | 62 | 29 min | model_stopped | 75 |
| 27b board v3 | 77 | 36 min | done_signal ⭐ | **92** |
| coder board v1 | 87 | 11 min | done_signal ⭐ | **88** |
| coder board v2 | 73 | 9 min | done_signal ⭐ | **88** |
| coder board v3 | 125 | 16 min | done_signal ⭐ | **95** |
| 35ba3b board v1 | 98 | 15 min | done_signal ⭐ | **85** |
| 35ba3b board v2 | 66 | 11 min | api_error: 400 | 35 |
| 35ba3b board v3 | 57 | 8 min | model_stopped | 40 |

### Mean and range, by (model × task)

| | mean | best | worst | spread |
|---|---:|---:|---:|---:|
| 27B memo | 48 | 85 | 10 | 75 |
| 27B board | **86** | 92 | 75 | 17 |
| Coder-Next memo | 32 | 80 | 5 | 75 |
| Coder-Next board | **90** | 95 | 88 | 7 |
| 35B-A3B memo | 6 | 10 | 3 | 7 |
| 35B-A3B board | **53** | 85 | 35 | 50 |

**Memo task spread is much wider than board task spread for the dense/agent models.** Coder-Next board: range of 7. Coder-Next memo: range of 75. Variance isn't a constant property of the model — it depends on the task structure.

## Three takeaways

### 1. Bounded structured input dramatically reduces variance and increases success

The board task input is a fixed git repo. The agent doesn't have to "go pick a company" — it inherits one. The agent doesn't have to "go find the data" — it's mounted at `/input/repo/`. Most of the search-the-world variance source from the memo task is eliminated.

Result: every model is meaningfully better on the board task. The 35B-A3B went from 0/3 to 1/3 — its first-ever success in this batch. Coder-Next went from 1/3 to perfect 3/3. The 27B's bad runs improved (worst 10→75 between memo and board).

**This validates the hypothesis from the memo-task variance findings doc**: the high variance we observed earlier was substantially task-design variance, not model variance.

### 2. The success-rate-vs-best-score metric pulls in different directions

Coder-Next on the board task: 3/3, mean 90, best 95. **The most reliable model on the most-reliable task.**

27B-AWQ on the memo task: 1/3, mean 48, best 85. When it works, it produces our highest-quality single deliverable (4-run/14-alternative ADR, 2K-word memo, 6-sheet xlsx). When it doesn't, it really doesn't.

If you're optimizing for **reliability** (probability of a usable deliverable), Coder-Next on the board task is the clear pick. If you're optimizing for **ceiling** (best possible deliverable), 27B-AWQ on either task is competitive — but you have to be willing to retry.

### 3. Failure modes are model-specific, not task-specific

| failure mode | 27B-AWQ | Coder-Next | 35B-A3B |
|---|---|---|---|
| stuck (no progress) | – | 2× memo | 1× memo |
| model_stopped (no done()) | 1× memo, 1× board | – | 2× (1 each task) |
| api_error timeout (>60min single call) | 1× memo | – | – |
| api_error 400 (context overflow) | – | – | 1× board |
| exceeded_max_tokens_cap | – | – | 1× memo |
| parser fault mid-emission | 1× memo | – | – |

- **27B-AWQ** dies on long thinking and parser edge cases (when it works, it works hard)
- **Coder-Next** dies on getting stuck after scaffolding (when it doesn't get stuck, it ships fast and clean)
- **35B-A3B** dies in many different ways (six runs across both tasks: stuck, give-up-early, max-tokens-cap, model-stopped, api-400 — it's the least stable of the three)

## Per-model judgment

### 27B-AWQ (Qwen3.6 dense, thinking mode)

- **The deliberate analyst.** Long single-call thinking. Few large commits. Rich per-artifact content (multi-source trace cross-checks, full reconciliation chains, more dead-ends).
- Strongest on the memo task when it succeeds (best-ever single deliverable, 14-alternative ADR, 2K-word memo).
- Failures often look like "real progress that didn't quite finish" — got cut off by parser or timeout, not stuck in loops.
- Use when: you can afford retries and want highest ceiling.

### Coder-Next-AWQ (Qwen3-Coder-Next MoE 80B/3B, no thinking)

- **The production engineer.** Granular commits, fast, lean artifacts. 4× faster than 27B per run.
- Most reliable on the board task. Most reliable across both tasks combined.
- Failures look like "scaffold and stop" — the dominant failure mode is making the directory structure + ADR placeholders then getting into a tight loop without producing real content.
- Use when: you need predictable production-quality output without retries.

### 35B-A3B-AWQ (Qwen3.6 35B/3B MoE, thinking mode)

- **Marginal on this hardware/precision.** 1/6 across both tasks.
- Failure modes are diverse — different fault every time (six runs, six different failures).
- Single success (35B board v1) was solid (~85) — when it works it can ship, but you can't predict when.
- Different commit-message style (Conventional Commits: "feat:", "docs:", "draft:") — only model in the batch to do this. Suggests its training data leaned heavier into specific repo conventions.
- Use when: you need diversity in approach for ensemble methods. Don't use as a primary single-shot agent.

## Cost / speed table (averaged across the 3 runs)

| | mean wall (memo) | mean tokens (memo) | mean wall (board) | mean tokens (board) |
|---|---:|---:|---:|---:|
| 27B | 36 min | 32K | 33 min | 45K |
| Coder-Next | 5 min | 23K | 12 min | 50K |
| 35B-A3B | 5 min | 33K | 11 min | 54K |

Coder-Next averages **~3× faster wall time** than 27B with comparable token output. Hardware utilization story: dense 27B is bandwidth-bound, MoE models with 3B active params are compute-light per token but generate more tokens.

## What we still don't know

- **N=3 is borderline.** Confidence intervals on a 1/3 success rate are wide ([1%, 71%] at 95%). Coder-Next board's 3/3 puts the lower bound at ~30% but doesn't pin a real expected rate. **N≥10 would be the right next batch** if we want defensible confidence intervals.
- **Cross-input variance**: would these models do similarly well building a deck from the *Coder-Next DocuSign* memo? Different input quality (PT-vs-DCF inconsistency, fewer ADR alternatives, fewer transcripts) might surface different agent behaviors. Untested.
- **Pipeline composition**: this batch only ran agent_2 with input from agent_1's *successful* run. What if you feed it from a partial/failed run? Probably tells you whether the pipeline is robust or whether quality compounds in either direction.
- **Cross-task transfer**: does failure mode predict failure mode? E.g., if a model fails on memo task, does it fail similarly on board task? Sample is too small to tell.

## Suggested next moves

1. **N=10 on the highest-signal cell** (Coder-Next × board task) to bound the success rate confidence interval. ~2 hours of compute.
2. **Run agent_2 on Coder-Next's DocuSign memo** as input — see how input quality affects deliverable quality.
3. **Add a third task type** that should differentiate models the other way (e.g., a code-refactor task where Coder-Next's MoE specialty shows up clearly).
4. **Stop here and write the formal report.** We have enough signal to make defensible recommendations for use cases.

## Receipts and artifacts

All 18 runs have:
- `agent-pilot/logs/<run>/receipt.json` — full reproducibility metadata
- `agent-pilot/logs/<run>/transcript.jsonl` — every model turn + tool call
- `agent-pilot/logs/<run>/summary.json`
- `agent-pilot/logs/<run>/workspace_final.tar.gz`

Canonical deliverables (the 8 successful runs that hit `done_signal` + produced content):
- `agent-pilot/canonical-deliverables/27b-awq-gtlb/` (memo)
- `agent-pilot/canonical-deliverables/coder-next-docu/` (memo)
- `agent-pilot/canonical-deliverables/27b-awq-board-deck-gtlb/` (board, v1)
- `agent-pilot/canonical-deliverables/coder-next-board-deck-gtlb/` (board, v1)
- *(plus 4 more boards extractable on request: 27B v3, Coder-Next v2/v3, 35B v1)*
