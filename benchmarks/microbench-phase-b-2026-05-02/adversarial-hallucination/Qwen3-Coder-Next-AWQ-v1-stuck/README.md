# Adversarial hallucination — Qwen3-Coder-Next-AWQ (Next-AWQ-v1-stuck)

> Representative `stuck_no_workspace_change_for_500_iters` (pathology).
>
> This run hit the harness's 500-iter workspace-hash threshold without writing the spec output. For Coder-Next, this is the modal failure mode on this cell — see [`../README.md`](../README.md) for the cell ship rate and pathology distribution.

## What ran

- **Task**: Classify 15 issues (6 real / 9 fabricated) — resistance to confident-but-wrong claims.
- **Model**: `v1` (no `--no-think` flag)
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `stuck_no_workspace_change_for_500_iters` |
| Wall time | 1557 s |
| Iterations | 500 |
| Completion tokens | 48,883 |
| Cost (upper-bound) | $0.0337 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p2_hallucination_coder_v1/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
