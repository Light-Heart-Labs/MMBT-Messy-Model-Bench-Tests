# PR #1025 — Verdict

> **Title:** fix(dashboard-api): wire Apple Silicon into /api/gpu/detailed
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/gpu-detailed-apple-silicon`
> **Diff:** +100 / -0 across 2 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1025

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Adds the missing `gpu_backend == "apple"` branch in `_get_raw_gpus` (`routers/gpu.py:60-65`) so `/api/gpu/detailed` returns 200 instead of 503 on Apple Silicon. The existing aggregate `get_gpu_info_apple()` is wrapped by a new `_apple_info_to_individual` helper that synthesizes a single `IndividualGPU` with `index=0` and `uuid="apple-unified-0"` (15 chars, satisfies the dashboard's `GPUCard.jsx .slice(-8)` key). Three new tests cover the wrap, `None`-propagation, and the full endpoint round-trip.

## Findings

- The `uuid="apple-unified-0"` choice is deliberately documented (comment + test assertion at `tests/test_gpu_detailed.py:368`) — defensible given the React key requirement and the unified-memory model. Stable string is appropriate since there's only ever one Apple GPU.
- `utilization_percent=0` and `temperature_c=0` are documented limitations (IOKit not accessible from this Python context). PR body explicitly scopes those out as future work — correct call.
- New `apple` branch is gated on exact string match (`gpu.py:60`); NVIDIA/AMD paths untouched. Zero risk to other platforms.

## Findings on conventions

- No new `eval`, `2>/dev/null`, `|| true`, or broad `except`. Existing 503 propagation path is reused unchanged.

## Cross-PR interaction

- No file overlap with other open PRs in this batch — `routers/gpu.py` and `tests/test_gpu_detailed.py` are not touched by the host-agent or extensions.py clusters.
- Cluster 1 (dream-cli) has Apple Silicon polish PRs (#999, #1016, #1020) but those are CLI-side, disjoint from `routers/gpu.py`.

## Trace

- `routers/gpu.py:18` — `get_gpu_info_apple` import
- `routers/gpu.py:42-54` — `_apple_info_to_individual` helper
- `routers/gpu.py:60-65` — new apple branch in `_get_raw_gpus`
- `tests/test_gpu_detailed.py:344-414` — fixture + 3 new tests
