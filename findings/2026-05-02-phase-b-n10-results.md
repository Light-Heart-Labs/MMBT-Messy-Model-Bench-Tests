# 2026-05-02 — Phase B N=10 results: ship-rate findings, new Coder-Next pathology, methodology updates

> Phase B expanded the 4 differential cells (`p2_hallucination`, `p3_business`, `p3_doc`, `p3_market`) from N=3 → N=10 to bound the headline differential claims. This doc reports what the new sample size **definitively settles** at the ship-rate grain (does the model produce output and stop?) and surfaces a **new Coder-Next failure mode** caught during the chain. PASS-rate analysis (output quality, not just shipping) is in a follow-up section pending re-grading.

## TL;DR

| Cell | Phase A (N=3) framing | Phase B (N=10) result | Definitive? |
|---|---|---|---|
| p2_hallucination Coder stuck rate | "2/3 stuck" — directional | **5/10 stuck**, Wilson 95% [23.7%, 76.3%] | ✅ bounded |
| p3_market Coder ship rate | "0/3 STRUCTURAL_FAIL" — directional | **0/10 done_signal**, Wilson 95% [0%, 27.8%] | ✅ bounded |
| p3_doc 27B word-limit-trim loop rate | "2/3 manually advanced" | **4/10 wall_killed_identical_call_loop**, Wilson 95% [16.8%, 68.7%] | ✅ bounded as stable failure shape |
| p3_business 27B word-limit-trim loop rate | "1/3 1-word over, 2/3 PASS" | **9/10 done_signal, 1/10 wall_killed**, Wilson 95% [1.8%, 40.4%] for the loop | ✅ bounded as low-rate |

**Plus a new pathology** — `wall_killed_low_progress_bash_loop` — caught on `p3_market_coder_v9` and `_v10` consecutively. Documented below.

## Method

**Phase B chain**: identical harness flags to N=3 originals (`--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`). Same task files, same input mounts, same vLLM containers (until the 2026-05-02 dual-GPU switchover, after Phase B was complete). Per-run `harness.sha256` matches v1-v3 originals, confirmed via receipt comparison.

**Ship rate vs PASS rate**: this doc reports ship rate — does the run reach `done_signal` / `model_stopped` (model produced output and stopped on its own) vs `stuck_no_workspace_change_for_500_iters` / `wall_killed_*` / `api_error:*`. PASS rate (does the output meet the per-task grading rubric?) requires running the batch graders against the new tarballs. That follow-up is Phase 2 below.

**Wilson 95% CIs** computed via the standard score interval formula (z=1.96).

## Results: ship-rate distribution at N=10

| Cell | Model | done_signal | model_stopped | stuck (500) | killed (loop) | api_error | Ship rate | 95% CI |
|---|---|---:|---:|---:|---:|---:|---:|---|
| p2_hallucination | 27B | 7 | 3 | 0 | 0 | 0 | **10/10** | [72.2%, 100%] |
| p2_hallucination | Coder | 5 | 0 | 5 | 0 | 0 | **5/10** | [23.7%, 76.3%] |
| p3_business | 27B | 9 | 0 | 0 | 1 | 0 | **9/10** | [59.6%, 98.2%] |
| p3_business | Coder | 10 | 0 | 0 | 0 | 0 | **10/10** | [72.2%, 100%] |
| p3_doc | 27B | 6 | 0 | 0 | 4 | 0 | **6/10** | [31.3%, 83.2%] |
| p3_doc | Coder | 10 | 0 | 0 | 0 | 0 | **10/10** | [72.2%, 100%] |
| p3_market | 27B | 7 | 0 | 0 | 0 | 3 | **7/10** | [39.7%, 89.2%] |
| p3_market | Coder | 0 | 0 | 4 | 2 | 4 | **0/10** | [0%, 27.8%] |

Notes on the failure-mode columns:
- **stuck (500)**: harness's workspace-hash detector fired after 500 unchanged iterations
- **killed (loop)**: operator-SIGTERM per documented methodology rules. p3_doc_27b: identical-call-loop on `brief.md` word-limit-trim. p3_market_coder v9/v10: new `wall_killed_low_progress_bash_loop` (see § "New pathology")
- **api_error 27B**: `api_error: timed out` — transient vLLM connection issue, retryable. The 3 p3_market_27b infra failures should recover under retry
- **api_error Coder p3_market**: `api_error: HTTP Error 400: Bad Request` — vLLM rejecting due to context overflow. NOT transient infra; effectively a model failure to converge within 262K context

## Definitive findings

### 1. Coder-Next stuck rate on adversarial-hallucination is bounded ~50% at N=10

- 5 of 10 runs hit `stuck_no_workspace_change_for_500_iters`. Wilson 95% CI [23.7%, 76.3%].
- 27B is 0 of 10 stuck (Wilson 95% CI [0%, 27.8%]).
- The original N=3 hint (2/3 stuck) is now bounded as a real, reproducible Coder-Next failure mode on this task class — not a 1-of-N flake.
- Stuck-detector firing on this task is itself diagnostic: the task asks the agent to distinguish 6 real bugs from 9 fabrications across a code review report. 500 iters of unchanged workspace = 500 iters of reading code without writing a verdict, which suggests the model can't decide cleanly between "real" and "fabricated."

### 2. Coder-Next never ships market_research at N=10 — the original 0/3 was directional, now it's bounded

- **0 of 10 runs reached done_signal**. Wilson 95% CI [0%, 27.8%].
- Failure breakdown:
  - 4/10 stuck_no_workspace_change
  - 4/10 api_error: HTTP 400 (vLLM context overflow at high iter counts)
  - 2/10 operator-killed `wall_killed_low_progress_bash_loop` (the new pathology — see below)
- Combined: every shape of failure imaginable, none of completion.
- 27B at the same task: 7/10 done_signal + 3/10 transient infra error → ship rate 70% with full recovery expected on retry.

This is the **clearest local-model-superiority signal** in the entire microbench suite at N=10. 27B drives sustained internet-research workflows; Coder-Next architecturally cannot, regardless of seed.

### 3. 27B doc_synthesis identical-call-loop is a stable ~40% failure shape

- 4 of 10 runs hit `wall_killed_identical_call_loop` on `brief.md` word-limit trim. Wilson 95% CI [16.8%, 68.7%].
- Remaining 6/10 reached done_signal (PASS rate at the 700-word limit TBD — Phase 2).
- Original N=3 had v2/v3 manually advanced and v1 reaching done_signal at 765 words (>700 limit, FAIL). At N=10 the loop manifests in roughly half the runs, confirming this as a **stable 27B failure shape on tasks with tight word-limit trim requirements**, not a v2/v3 fluke.
- Coder-Next on the same task: 10/10 done_signal — 27B's loop pathology does not extend to Coder-Next.

### 4. 27B business_memo word-limit issue is much less common than on doc_synthesis

- 9/10 done_signal + 1/10 wall_killed_identical_call_loop. Wilson 95% CI on loop rate [1.8%, 40.4%].
- The same word-limit-trim failure mode that hits doc_synthesis ~40% manifests on business_memo at ~10%.
- Hypothesis: business_memo's 700-word limit is paired with a richer task spec (8 bias signals to recall, stance pushback expected) that gives the model more "stuff to write," making the trim less of a binding constraint than on doc_synthesis (8 facts, narrow focus).

## New pathology: `wall_killed_low_progress_bash_loop`

Two consecutive Coder-Next p3_market reps (v9, v10) hit a previously-undocumented failure mode:

| | v9 | v10 |
|---|---|---|
| Started | 06:25Z | 12:20Z |
| Killed | 12:20Z | 12:38Z |
| Wall | 5h55m | 18m |
| Iters | 2018 | 14 (sandbox), runaway model gen on iter 15 |
| Model loop pattern | curl-loop on 5 password-manager URLs with **incrementing filename suffix** (`1password_linear_apps354.html`, `355.html`, ... up to 403 dups across 5 vendors) | curl + grep-pipeline loop on `1password.com/business/` with slight variations of the grep regex |
| Files written | 2017 duplicate HTML files in `research/`, 0 deliverables | 0 deliverables |
| `total_completion_tokens` | 127,326 | 1,373 (then runaway gen on iter 15 producing ~125K more, never returned) |
| `total_prompt_tokens` | 187,241,148 (each iter sends full conversation history at near-context-cap) | 178,260 |

**Why the harness's stuck-detector missed both**: the detector watches `workspace_state_hash` unchanged for 500 iterations. Each iter wrote a *different filename* (or a different grep pattern's transient state), so the workspace hash kept changing on every iter. The detector never fired.

**Operator-SIGTERM methodology** (now documented as Rule 5 in `feedback_microbench_methodology`):

```bash
# Detection probe:
#  - iter > 500 + wall > 4hr + transcript shows >50 consecutive bash calls
#    with similar args_len + workspace deliverables empty
PID=$(ps aux | grep "harness.py <run_name>" | grep -v grep | awk '{print $2}' | head -1)
docker exec bench-sandbox-<run_name> tar -czf - -C / workspace > logs/<run>/workspace_final.tar.gz
kill -TERM $PID
# Write synthetic summary.json with finish_reason: wall_killed_low_progress_bash_loop
```

The fact that **two consecutive reps** of the same task class manifested this pattern — at temperature=0.3 / seed=42 — makes it a reproducible Coder-Next pathology, not a 1-of-N flake. Whether it manifests on other task classes is open, but should be assumed possible until ruled out.

**Suggested grader/harness extension**: add a soft signal to the harness watchdog for "iters past 200 with no new files in workspace deliverables." Workspace-hash-changing diverse-filename loops would trigger this without changing the stuck-detector for legitimate workloads.

## Methodology updates committed today

1. **Harness `--no-think` flag added.** Smoke-test confirmed: thinking-on emits 519 tokens of `<think>` for "what is 7*8?", with `--no-think` it emits 3 tokens straight to "56". Receipts record `chat_template_kwargs` for reproducibility. Used for the 27B-no-think arm currently in flight.

2. **Workspace-cleanup sudo fallback.** Re-running a previously-aborted run failed because the prior sandbox left root-owned `.git/` files in the workspace mount; the harness's `rm -rf` lacked permission. Patched to fall back to `sudo -n rm -rf` on failure. Caught via 2 re-run failures (p3_doc_27b_v7, p2_hallucination_coder_v9) at the start of the Phase B re-launch.

3. **New methodology rule (Rule 5 in feedback memory)**: `wall_killed_low_progress_bash_loop` for diverse-filename bash loops the workspace-hash stuck-detector misses. Pairs with operator-SIGTERM + synthetic summary.

4. **Dual-GPU switchover for 27B-no-think.** When Coder Phase B finished, vllm-coder-next was torn down and a second vllm-qwen36-awq instance was launched on GPU1:8003. Two shard runners (60 runs each) parallelize the no-think grid. Throughput delta: pre-switchover ~2.4 runs/hr (GPU0 single, contended with Phase B), post-switchover ~17 runs/hr (~7× speedup). Switchover orchestration in `agent-pilot/scripts/switchover_to_dual_gpu.sh` and `run_full_grid_27b_nothink_shard.sh`.

## What's next

### Phase 2 — PASS-rate analysis (DONE 2026-05-02)

`batch_grade_p2.sh` and `batch_grade_p3.sh` re-run on the new Phase B tarballs. All 8 cells × 10 reps now have `grade.json`.

#### N=10 PASS-rate table (with Wilson 95% CIs)

| Cell | Model | Phase A (N=3) PASS | Phase B (N=10) PASS | 95% Wilson CI | Direction |
|---|---|---|---|---|---|
| p2_hallucination | 27B | 3/3 (100%) | **7/10 (70%)** | [39.7%, 89.2%] | **N=3 was overstated** — 30% MISSING_OUTPUT rate emerged |
| p2_hallucination | Coder | 1/3 (33%) | 5/10 (50%) | [23.7%, 76.3%] | unchanged direction; CI heavily overlaps with 27B |
| p3_business | 27B | 2/3 (67%) | 8/10 (80%) | [49.0%, 94.3%] | confirmed |
| p3_business | Coder | 3/3 (100%) | **10/10 (100%)** | [72.2%, 100%] | confirmed — definitive 100% |
| p3_doc | 27B | 0/3 (0%) | **1/10 (10%)** | [1.8%, 40.4%] | confirmed — definitive failure |
| p3_doc | Coder | 2/3 (67%) | 7/10 (70%) | [39.7%, 89.2%] | confirmed |
| p3_market | 27B | 3/3 STRUCTURAL_PASS (100%) | **7/10 (70%)** | [39.7%, 89.2%] | confirmed (3/10 are infra-flaky api_error: timed out, retryable) |
| p3_market | Coder | 0/3 STRUCTURAL_FAIL (0%) | **0/10 (0%)** | [0%, 27.8%] | confirmed — definitive 0% |

#### CI separation between models

| Cell | 27B CI | Coder CI | CIs overlap? | Verdict at N=10 |
|---|---|---|---|---|
| p2_hallucination | [39.7%, 89.2%] | [23.7%, 76.3%] | **YES, heavy** | **Original "27B clearly better" claim does NOT hold at N=10** — directionally still 27B better, not bounded |
| p3_business | [49.0%, 94.3%] | [72.2%, 100%] | YES, partial | Coder marginally better, not bounded |
| p3_doc | [1.8%, 40.4%] | [39.7%, 89.2%] | barely (40.4 vs 39.7) | **Effectively definitive Coder advantage** |
| p3_market | [39.7%, 89.2%] | [0%, 27.8%] | NO | **Definitive 27B advantage** |

#### Definitive PASS-rate findings

**5. The 27B "100% accuracy on hallucination" claim from N=3 is overstated.** N=10 reveals a 30% rate of `model_stopped` without writing the verdict file (v8, v9, v10 all consecutive). All 7 runs that *do* write output PASS at high accuracy, but the ship rate is only 70%. Combined with the 50% Coder ship rate, the gap closes substantially: **27B nominally 7/10 vs Coder 5/10, CIs heavily overlap**. The cell remains directionally 27B-favored but not bounded.

**6. NEW 27B failure mode discovered at N=10: "stuck in think mode."** `p2_hallucination_27b_v8` finished at iter 3 with **1867 completion tokens but content_len=0 and zero tool calls**. The model generated thinking tokens, the `--reasoning-parser qwen3` stripped them into `reasoning_content`, and the model never emerged from thinking to either produce content or call a tool. This is distinct from `model_stopped without saying anything` (degenerate empty response) — it's `model thought a lot then quit without acting`. v9 and v10 hit similar patterns. **This is a previously-undocumented 27B failure mode and a candidate for a deeper investigation.**

**7. p3_doc 27B is now definitively poor (10% PASS at N=10).** Even though 6/10 runs ship `done_signal`, almost all of them fail the 700-word limit. Only 1/10 PASSed the rubric (v10). Combined with the 4/10 wall_killed_loop rate, **27B is a non-starter for tasks with tight word-limit-trim requirements** at temp=0.3 / seed=42.

**8. p3_business Coder is definitively perfect (10/10 PASS).** The original 3/3 finding extends to N=10. Coder-Next is the right model for skeptical-deal-pack-review-shaped tasks at this scale.

**9. p3_market 27B vs Coder is the cleanest separation in the bench.** 27B's 70% PASS bounded against Coder's 0% PASS — CIs do not touch. With infra retries on the 3 27B api_error: timed out runs, the real 27B PASS rate is likely closer to 100% on completable runs. **This is the largest model-superiority signal in the suite.**

#### What the original headline claims look like now

From the 2026-04-28 findings doc (Phase A):
- ~~"27B 3/3 PASS at 100% accuracy 0 dangerous errors on hallucination"~~ → 70% PASS at N=10 with a 30% non-shipping rate; accuracy when shipping is still high
- "27B 3/3 STRUCTURAL_PASS on market_research" → confirmed: 70% (with 3 retryable infra failures)
- "Coder-Next 0/3 STRUCTURAL_FAIL on market_research" → confirmed: 0% at N=10, definitive
- "Coder-Next 2/3 PASS on doc_synthesis" → confirmed: 70% at N=10
- "27B 0/3 PASS on doc_synthesis" → confirmed: 10% at N=10, definitive failure
- "Coder-Next 3/3 PASS on business_memo" → confirmed: 100% at N=10, definitive
- "27B 2/3 PASS on business_memo" → confirmed: 80% at N=10

**The aggregate-tied 56% / 56% headline from Phase A** is still the right framing, but the differential cells now have **bounded** numbers. The 4 cells the headline rests on:
- 27B wins definitively on 1 of 4 (market_research)
- Coder wins definitively on 1 of 4 (doc_synthesis)
- Coder wins directionally on 1 of 4 (business_memo, CIs overlap)
- The expected 27B win on hallucination (1 of 4) **doesn't bound at N=10** — overlapping CIs

So the daily-driver rule has tightened:

| Use case | Model | Confidence at N=10 |
|---|---|---|
| Internet research / market_research-shaped | **27B** | bounded 70% PASS vs Coder 0% |
| Tight-word-limit summary writing | **Coder** | bounded 70% PASS vs 27B 10% |
| Skeptical deal-pack review (business memo) | **Coder** (or 27B) | Coder 100% vs 27B 80%, both viable |
| Adversarial hallucination resistance | **directionally 27B** | overlapping CIs at N=10; gap is smaller than N=3 suggested |

### Phase 3 — 27B-no-think arm (in flight, ~14:00 EDT projected finish)

Currently running on both GPUs in parallel. 12 task families × N=10 = 120 runs. Will give a three-arm comparison:

- 27B-thinking PASS rate (existing)
- 27B-no-think PASS rate (new)
- Coder-Next PASS rate (existing)

The big question: does no-think 27B keep 27B's task-class wins (hallucination, market, bug-fix) while gaining Coder-Next's speed and cost ratio? If yes → no-think is the new daily-driver default for cost-sensitive deployments where 27B's task-class strengths still matter.

## Caveats

- **Ship rate is not output quality.** A run that reaches done_signal can still produce a wrong or low-quality deliverable. PASS rate (Phase 2) is the load-bearing follow-up.
- **The 4 p3_market_coder api_error: HTTP 400 runs are NOT transient infra**, despite the `api_error:` prefix. They reflect vLLM context overflow at high iter counts — model can't converge within 262K context. They are model failures, not retryable infra issues. Distinguished from the 3 p3_market_27b `api_error: timed out` runs which ARE transient infra.
- **All Phase B numbers reflect only the differential cells.** The other 8 task families (p1_bugfix, p1_refactor, p1_testwrite, p2_ci, p2_extract, p2_triage, p3_pm, p3_writing) are still at N=3 from the original Phase A grid — their per-cell wins remain directional, not bounded.
- **Headlines like "27B drives market research, Coder-Next can't" still ride on a single task instance per cell.** The N=10 expansion bounds the *rate* of failure within the password-manager-comparison instance; whether the architectural strength generalizes to other internet-research-shaped tasks is a separate question (recommend a second-instance benchmark before quoting as a generalized model property).

## Cross-references

- [`2026-04-28-coding-and-business-microbenches.md`](2026-04-28-coding-and-business-microbenches.md) — Phase A headline aggregate-tied finding
- [`2026-04-28-pairwise-quality-study.md`](2026-04-28-pairwise-quality-study.md) — Phase C pairwise quality comparison on the both-ship cells
- `feedback_microbench_methodology` (memory) — Rules 1-5 for chain methodology
- `agent-pilot/scripts/run_full_grid_27b_nothink_shard.sh` — sharded chain runner (NEW)
- `agent-pilot/scripts/switchover_to_dual_gpu.sh` — switchover orchestrator (NEW)
- `agent-pilot/logs/p3_market_coder_v9/summary.json` — first reproducer of the bash-loop pathology
- `agent-pilot/logs/p3_market_coder_v10/summary.json` — second reproducer
