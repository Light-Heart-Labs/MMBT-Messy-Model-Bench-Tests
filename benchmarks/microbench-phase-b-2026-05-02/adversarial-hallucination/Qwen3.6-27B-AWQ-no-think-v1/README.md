# Adversarial hallucination — Qwen3.6-27B-AWQ (no-think) v1

> Representative `done_signal` run for this cell. Shown here so a reader can see *one* concrete artifact set per task family without drilling into the source bench's submit branch.

## What ran

- **Task**: Classify 15 issues (6 real / 9 fabricated) — resistance to confident-but-wrong claims.
- **Model**: `qwen3.6-27b-awq` with `--no-think` flag
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all --no-think`

## Outcome

| | |
|---|---|
| `finish_reason` | `done_signal` |
| Wall time | 105 s |
| Iterations | 16 |
| Completion tokens | 5,143 |
| First-write latency | 56.1 s |
| Cost (upper-bound) | $0.0019 |

## What's published here

The 5 metadata files (`cost.json`, `grade.json`, `label.json`, `receipt.json`, `summary.json`) are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p2_hallucination_27b-nothink_v1/`.

## Cross-references

- [`../README.md`](../README.md) — task-level summary with all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
