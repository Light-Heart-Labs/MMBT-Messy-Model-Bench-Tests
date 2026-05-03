# Market research — Qwen3.6-27B-AWQ (thinking) (v?)

> Representative `done_signal` run.
>
> Shown as the canonical clean ship for this (cell × model).

## What ran

- **Task**: Evaluate 5 password-manager products with live-network research and citations.
- **Model**: `v1` (thinking-mode (default))
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `done_signal` |
| Wall time | 1037 s |
| Iterations | 71 |
| Completion tokens | 30,141 |
| First-write latency | 8.2 s |
| Cost (upper-bound) | $0.0225 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_market_27b_v1/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
