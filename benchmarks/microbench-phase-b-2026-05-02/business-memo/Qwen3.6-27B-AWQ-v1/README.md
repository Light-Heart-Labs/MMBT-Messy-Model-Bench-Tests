# Business memo — Qwen3.6-27B-AWQ (thinking) (v?)

> Representative `done_signal` run.
>
> Shown as the canonical clean ship for this (cell × model).

## What ran

- **Task**: Read an acquisition deal pack; catch 8 planted bias signals; push back; ≤700 words.
- **Model**: `v1` (thinking-mode (default))
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `done_signal` |
| Wall time | 170 s |
| Iterations | 16 |
| Completion tokens | 9,589 |
| First-write latency | 19.5 s |
| Cost (upper-bound) | $0.0037 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_business_27b_v1/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
