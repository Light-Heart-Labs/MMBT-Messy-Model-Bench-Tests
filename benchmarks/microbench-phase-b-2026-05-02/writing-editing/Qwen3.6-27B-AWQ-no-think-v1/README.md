# Writing/editing — Qwen3.6-27B-AWQ (no-think) v1

> Representative `done_signal` run for this cell. Shown here so a reader can see *one* concrete artifact set per task family without drilling into the source bench's submit branch.

## What ran

- **Task**: Audience-tailored rewrite with per-audience must-include / must-not-include.
- **Model**: `qwen3.6-27b-awq` with `--no-think` flag
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all --no-think`

## Outcome

| | |
|---|---|
| `finish_reason` | `done_signal` |
| Wall time | 132 s |
| Iterations | 24 |
| Completion tokens | 6,715 |
| First-write latency | 14.6 s |
| Cost (upper-bound) | $0.0024 |

## What's published here

The 5 metadata files (`cost.json`, `grade.json`, `label.json`, `receipt.json`, `summary.json`) are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_writing_27b-nothink_v1/`.

## Cross-references

- [`../README.md`](../README.md) — task-level summary with all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
