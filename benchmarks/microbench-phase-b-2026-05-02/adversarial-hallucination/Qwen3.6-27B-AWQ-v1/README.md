# Adversarial hallucination — Qwen3.6-27B-AWQ (thinking) (v?)

> Representative `done_signal` run.
>
> Shown as the canonical clean ship for this (cell × model).

## What ran

- **Task**: Classify 15 issues (6 real / 9 fabricated) — resistance to confident-but-wrong claims.
- **Model**: `v1` (thinking-mode (default))
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `done_signal` |
| Wall time | 171 s |
| Iterations | 10 |
| Completion tokens | 10,030 |
| First-write latency | 129.0 s |
| Cost (upper-bound) | $0.0037 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p2_hallucination_27b_v1/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
