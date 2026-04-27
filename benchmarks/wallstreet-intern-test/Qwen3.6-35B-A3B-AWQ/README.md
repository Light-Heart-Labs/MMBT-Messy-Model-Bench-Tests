# Wallstreet Intern Test — Qwen3.6-35B-A3B-AWQ (NO USABLE DELIVERABLE)

**Auditor:** Qwen3.6-35B-A3B AWQ-4bit (Cyankiwi quantization), MoE 35B / 3B active, thinking-mode
**Audit date:** 2026-04-26
**vLLM config:** `--max-model-len 262144`, `--temperature 0.0`, `--reasoning-parser qwen3 --tool-call-parser qwen3_xml`

## This entry intentionally has no deliverable

The model attempted the task **three times**, none of them produced a usable memo:

| run | wall | iters | finish | what was produced |
|---|---|---|---|---|
| `35ba3b_invest_memo_v1` | 6 min | 51 | stuck (no workspace change for 30 iters) | mostly empty workspace; failed to transition from research to writing |
| `35ba3b_invest_memo_v2` | <1 min | 14 | model_stopped | nearly nothing — model stopped emitting tool calls almost immediately |
| `35ba3b_invest_memo_v3` | 7 min | 38 | exceeded_max_tokens cap | hit the per-response token cap mid-emission; only `tool-log.md` and a git scaffold made it into the workspace |

The folder is kept because the *kinds* of failure are themselves comparison data against the cloud entries (`GPT-5.5/`, `Opus-4.7/`) that *did* ship full memo packages on this same benchmark.

## What this means alongside the rest of the 35B-A3B record

35B-A3B-AWQ has now produced no usable deliverable on the two task families we've benchmarked:

- **`wallstreet-intern-test`**: 0/3 across `35ba3b_invest_memo_v{1,2,3}` (this folder)
- **`dreamserver-1-pr-audit`**: 0/1 ([`../../dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/`](../../dreamserver-1-pr-audit/Qwen3.6-35B-A3B-AWQ/) — floor failure: 28 iters of investigation then a 25-second thinking turn that emitted no tool call and stopped)
- **`dreamserver-75-pr-audit`**: not run after the N=1 floor failure made it clear larger scope wouldn't change the outcome

The earlier 2026-04-26 consolidated grid (memo + board × three replicates) had it at 1/6 across both task families. The 1 success was a single board-task run; for the agentic deliverable-shaped tasks in MMBT, 35B-A3B has effectively 0/9 across all evidence.

The model is a Qwen3.6 thinking-mode MoE with 35B total / 3B active params, quantized to 4-bit AWQ. The behavioral profile across all three memo runs:

- **v1**: did legitimate research (cloned ticker data, fetched filings) but couldn't transition to memo composition. Stuck-detector fired.
- **v2**: emitted ~14 tool calls in 14 seconds, then stopped. Effectively a floor failure at the smallest scale.
- **v3**: started writing actual content, hit the per-response max-tokens ceiling mid-thinking, and finished its response but never recovered to produce a complete memo. The cap was 64,000 tokens at the time (later raised to 180,000 in the harness changelog) — but a thinking-mode model that needs >64K tokens to compose a memo is a sign of a different problem (analysis ineffi­cient enough that the answer doesn't fit in available budget).

For someone considering 35B-A3B-AWQ for messy long-form work: the evidence in this repo argues against it. Higher-precision quantizations (FP8, BF16) might help — untested.

## Reproducibility

To attempt a replay (expect failure-shaped output):
```bash
python3 agent-pilot/harness.py replay_35ba3b_invest_memo_v3 \
  agent-pilot/task_investment_memo.md \
  --model qwen3.6-35ba3b-awq --port 8001 \
  --temperature 0.0
```

Receipts + transcripts for all three failed runs are kept in `agent-pilot/logs/35ba3b_invest_memo_v{1,2,3}/` in the source bench repo.
