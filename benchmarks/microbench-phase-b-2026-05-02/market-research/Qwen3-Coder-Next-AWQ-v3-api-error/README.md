# Market research — Qwen3-Coder-Next-AWQ (Next-AWQ-v3-api-error)

> Representative `api_error: HTTP Error 400: Bad Request` (pathology).
>
> Coder-Next filled vLLM's 262K-token context budget on this run without converging on a recommendation. Distinct from the workspace-hash stuck mode — this is a *context-overflow* failure where the model can't compress its accumulated research enough to keep generating. 4 of 10 Coder-Next p3_market runs hit this exact failure_reason at N=10.

## What ran

- **Task**: Evaluate 5 password-manager products with live-network research and citations.
- **Model**: `v3` (no `--no-think` flag)
- **Hardware**: Tower2, NVIDIA RTX PRO 6000 Blackwell, 500 W power cap
- **Harness**: `agent-pilot/harness.py` with `--temperature 0.3 --stuck-threshold 500 --docker-socket --gpus all`

## Outcome

| | |
|---|---|
| `finish_reason` | `api_error: HTTP Error 400: Bad Request` |
| Wall time | 391 s |
| Iterations | 65 |
| Completion tokens | 4,276 |
| First-write latency | 2.3 s |
| Cost (upper-bound) | $0.0085 |

## What's published here

The 5 metadata files are mirrored from the source bench. Transcripts and workspace tarballs are NOT mirrored here — they're in the source bench's `submit/phase-b-overnight-2026-05-02` branch at `agent-pilot/logs/p3_market_coder_v3/`.

## Cross-references

- [`../README.md`](../README.md) — cell-level summary with ship rates across all three models
- [`../../findings.md`](../../findings.md) — cross-task analysis
