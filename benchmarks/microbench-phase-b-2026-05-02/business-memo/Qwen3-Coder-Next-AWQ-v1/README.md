# Business memo — Qwen3-Coder-Next-AWQ (v?)

> Representative `done_signal` run.
>
> Shown as the canonical clean ship for this (cell × model).

## What ran

- **Task**: Read an acquisition deal pack; catch 8 planted bias signals; push back; ≤700 words.
- **Model**: `v1` (no `--no-think` flag)
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `done_signal` |
| Wall time | 32 s |
| Iterations | 12 |
| Completion tokens | 4,959 |
| First-write latency | 7.9 s |
| Cost (upper-bound) | $0.0007 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_business_coder_v1/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
