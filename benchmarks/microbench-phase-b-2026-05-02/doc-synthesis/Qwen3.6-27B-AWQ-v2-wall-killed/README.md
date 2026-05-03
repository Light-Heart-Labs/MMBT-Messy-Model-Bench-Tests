# Document synthesis — Qwen3.6-27B-AWQ (thinking) (AWQ-v2-wall-killed)

> Representative `wall_killed_identical_call_loop` (pathology).
>
> Harness wall-killed after detecting the model in an identical-call-loop. 4 of 10 27B-thinking runs on `p3_doc` hit this exact failure_reason at N=10 (the documented word-limit-trim loop where the model writes a draft, counts words, sees it's over 700, edits, recounts, and loops on the budget constraint). In `p3_doc` 27B-no-think, this drops to 2/10 — the most direct evidence that disabling thinking helps with the word-budget-retry pathology.

## What ran

- **Task**: Distill 12 PRs into a brief.md ≤700 words capturing 8 planted facts.
- **Model**: `v2` (thinking-mode (default))
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `wall_killed_identical_call_loop` |
| Wall time | 8129 s |
| Iterations | 159 |
| Completion tokens | 195,495 |
| First-write latency | 34.3 s |
| Cost (upper-bound) | $0.1761 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_doc_27b_v2/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
