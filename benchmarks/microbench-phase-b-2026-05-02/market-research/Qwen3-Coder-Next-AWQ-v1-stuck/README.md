# Market research — Qwen3-Coder-Next-AWQ (Next-AWQ-v1-stuck)

> Representative `stuck_no_workspace_change_for_500_iters` (pathology).
>
> This run hit the harness's 500-iter workspace-hash threshold without writing the spec output. For Coder-Next, this is the modal failure mode on this cell — see [`../README.md`](../README.md) for the cell ship rate and pathology distribution.

## What ran

- **Task**: Evaluate 5 password-manager products with live-network research and citations.
- **Model**: `v1` (no `--no-think` flag)
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `stuck_no_workspace_change_for_500_iters` |
| Wall time | 1146 s |
| Iterations | 502 |
| Completion tokens | 37,317 |
| First-write latency | 1.9 s |
| Cost (upper-bound) | $0.0248 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_market_coder_v1/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
