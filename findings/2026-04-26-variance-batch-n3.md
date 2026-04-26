# 2026-04-26 — Variance batch (N=3 per model)

> Three runs of each of three models on the same investment-memo task, same harness, same prompt, `temperature=0`. **Variance is enormous.** None of the three models reliably completes the task. Single-run scores are unsafe to use for comparison.

## Setup

- Task: `agent-pilot/task_investment_memo.md` (verbatim, no system prompt)
- Harness: per-run sandbox, dynamic max_tokens, stuck detector, ctok-based cap detection (added during this batch — see HARNESS-CHANGELOG.md)
- vLLM: `vllm/vllm-openai:latest` (`sha256:2622f38a…`) for all three models, identical container args within each model's runs (verified via receipts)
- All runs at `temperature=0`. Determinism is approximate due to vLLM bf16 cuBLAS workspace + batch reordering.

## Results

| model | run | iterations | wall | finish_reason | rough score | notable artifact |
|---|---|---|---|---|---|---|
| **27B-AWQ** | v2 | 56 | 28 min | `done_signal` | **~85** | GitLab memo, 6-sheet xlsx, 6 transcripts, 3 commits (canonical) |
| | v3 | 40 | 11.5 min | `model_stopped` (qwen3_xml parser failure) | ~50 | SentinelOne, 3 commits, real SEC filings (3× 10-K, 4× 10-Q, 5× 8-K), then model emitted text-style tool-call markup parser didn't catch |
| | v4 | 45 | 68 min | `api_error: timed out` (single call >60 min) | ~10 | HIMS, 1 commit, scaffolding only — model stalled mid-call |
| **Coder-Next** | v5 | 95 | 10.7 min | `done_signal` | **~80** | DocuSign memo, 3-sheet xlsx, 4 real iXBRL SEC filings, 19 commits (canonical) |
| | v6 | 37 | 2.1 min | `stuck` | ~5 | Picked nothing real, 1 commit, tight loop emitting same 474 tokens |
| | v7 | 63 | 1.8 min | `stuck` | ~10 | Nutanix, 8 scaffolding commits, no substantive work |
| **35B-A3B** | v1 | 51 | 6.4 min | `stuck` | ~10 | GitLab pick + 14-alt ADR, then looped on 5 identical 224 KB SEC homepage HTMLs |
| | v2 | 14 | 0.2 min | `model_stopped` | ~3 | 0 commits, scaffolded dirs then quit |
| | v3 | 38 | 7.4 min | `model_exceeded_max_tokens_64000` | ~5 | 1 commit, then emitted 64K-token single turn that hit the cap |

## Per-model success picture

|  | success rate (≥70/100) | scores observed | range |
|---|---|---|---|
| **27B-AWQ** | 1 / 3 | 85 / 50 / 10 | 75-point spread |
| **Coder-Next** | 1 / 3 | 80 / 10 / 5 | 75-point spread |
| **35B-A3B** | 0 / 3 | 10 / 5 / 3 | 7-point spread (all failures) |

## Failure-mode taxonomy

Both completing models (27B, Coder-Next) showed roughly the same success rate (1/3). Where they differ is in **what failure looks like**:

**27B-AWQ failure modes**
1. Parser failure mid-emission (v3): model emits text-style tool-call markup that vLLM's `qwen3_xml` parser doesn't extract. Real work happened first (3 commits, 12 SEC filings), then the conversation goes off the rails.
2. Long-think timeout (v4): single inference call exceeded the 60-min urlopen budget. Either genuine model stalling on a hard step or vLLM-side hang. No way to distinguish without instrumentation.

**Coder-Next failure modes**
1. Scaffold-and-stuck (v6, v7): completes the directory structure + ADR placeholders, then gets into a tight loop emitting near-identical short turns with no file changes. Stuck-detector fires within minutes.

**35B-A3B failure modes (all three different)**
1. Tool-output verification failure (v1): downloaded 5 files claiming to be 10-Ks but they were all the same 224 KB SEC.gov homepage HTML. Never inspected what came back.
2. Give-up-early (v2): emitted no content + no tool call at iter 14, vLLM returned `stop`. Effectively quit.
3. Single-turn cap explosion (v3): emitted 64,000 tokens in a single turn, hit the harness max_tokens cap, aborted cleanly by the new ctok-based detector.

The 35B-A3B's three different failure modes from N=3 is a striking finding — it doesn't even fail consistently. Suggests this model's behavior on this task is closer to a coin flip across multiple unstable equilibria than a "the model can/can't do it" determination.

## Implications

### N=1 is dangerous for ranking
The earlier "Coder-Next ~80, 27B ~85" comparison was based on the lucky run from each. The mean (or median) is much lower. With N=3:
- 27B median: ~50 (the parser-fault run)
- Coder-Next median: ~10 (one of the stuck runs)
- 35B-A3B median: ~5

If we'd ranked on median, 27B would still be ahead but the gap between models would be smaller AND the absolute scores would all be terrible — telling a very different story than "two competitive models around 80–85".

### N=3 is also too few
We see 1/3 success for both 27B and Coder-Next. The 95% CI on a 1/3 binomial is roughly [1%, 71%]. We can't even confidently say either model has >50% success rate from this batch. **Real comparisons need N=10+.**

### Harness bugs found mid-batch
This batch surfaced three distinct harness bugs that needed fixing on the fly:
1. `argv-length` — model emitted bash heredoc longer than ~128 KB; fixed via stdin pipe (commit `c60acfe`)
2. `UnicodeDecodeError` — model piped binary content (gzip magic) to stdout; fixed via `errors='replace'` (commit `5e2cd6b` era)
3. `ctok-cap-detection` — vLLM reports `finish_reason="tool_calls"` even when the model hit max_tokens on a tool-call-emitting turn; fixed by checking ctok against cap (commit `b98e3sjsq` era)

Plus one that's fixed but worth flagging: **the `inference_request_defaults.max_tokens_strategy` field in receipts was hardcoded text and went stale** when the cap value changed. Subtle reproducibility hazard if you trust receipts blindly.

### What the data suggests about the models, not the harness

After accounting for harness fixes:

- **27B-AWQ** is the strongest of the three on this task, but still only succeeds 1/3 of the time. When it works, it works well (~85). When it fails, the failures are usually meaningful work that runs into a parser or timeout edge case — not "the model can't do it" but "the model + this exact infrastructure breaks down in specific ways".

- **Coder-Next-AWQ** can succeed (v5 ~80) but its dominant failure mode is a fast scaffold-and-stop pattern (~5–15) that suggests it's not a thinking-mode model and lacks the planning depth this task rewards. It's still 1/3 success, but the failures are shallower — gives up faster.

- **Qwen3.6-35B-A3B-AWQ** failed all three runs in three different ways. This is consistent with the model being marginal for this task at this precision and instability across runs reflecting its operating near a capability boundary.

### What to do with these results

The right next step is **not** to rank these models on this task. The right next step is one of:

1. **N=10+ runs per model** to bound variance with confidence intervals. ~30 more runs at ~5–30 min each = several hours of compute. Doable.
2. **Add a different task** (coding, math, structured Q&A) where success/failure is sharper, see if these same models look different.
3. **Stop trying to rank and instead score the *distribution*** — % completion, median score, failure-mode breakdown — rather than the single "score".

Recommend (1) for the existing task plus (2) for breadth.

## Receipts and artifacts

Each run has its own:
- `agent-pilot/logs/<run>/receipt.json` — full reproducibility metadata
- `agent-pilot/logs/<run>/transcript.jsonl` — every model turn + tool call
- `agent-pilot/logs/<run>/summary.json` — final-state summary
- `agent-pilot/logs/<run>/workspace_final.tar.gz` — the agent's repo state at termination

Existing canonical deliverables (the two completed runs):
- `agent-pilot/canonical-deliverables/27b-awq-gtlb/` — 27B v2's GitLab memo
- `agent-pilot/canonical-deliverables/coder-next-docu/` — Coder-Next v5's DocuSign memo
