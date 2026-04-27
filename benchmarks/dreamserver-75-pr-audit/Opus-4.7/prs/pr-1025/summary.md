# PR #1025 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard-api): wire Apple Silicon into /api/gpu/detailed

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Wire Apple Silicon GPU detection into `/api/gpu/detailed` so the endpoint returns real data instead of a 503 on macOS.

## Why
`_get_raw_gpus` in `routers/gpu.py` only had a branch for `amd`, then fell through to NVIDIA/AMD sysfs probing — both return `None` on macOS, yielding an empty list. The existing `get_gpu_info_apple()` call (already used by `/api/features`) was never consulted, so every call to `/api/gpu/detailed` on Apple Silicon returned `503 No GPU data available`.

## How
- `routers/gpu.py`: import `get_gpu_info_apple` alphabetically into the existing `from gpu import (...)` block; add private helper `_apple_info_to_individual(info: GPUInfo) -> IndividualGPU` that wraps the aggregate `GPUInfo` into a single `IndividualGPU` with `index=0` and `uuid="apple-unified-0"` (≥8 chars, satisfies `GPUCard.jsx .slice(-8)` key requirement); add `"apple"` as the first branch in `_get_raw_gpus`, returning `[_apple_info_to_individual(info)]` or `None` if detection fails (propagates to the existing 503 path).
- `tests/test_gpu_detailed.py`: new fixture `_sample_apple_gpu_info()`; 3 new tests covering single-entry return, `None`-propagation, and full endpoint 200 response with Apple aggregate data.

## Testing
- Automated: `pytest tests/test_gpu_detailed.py -k "not history"` — 19/19 pass; ruff clean.
- Manual: On Apple Silicon Mac, `curl -H "Authorization: Bearer $DASHBOARD_API_KEY" http://localhost:$DASHBOARD_API_PORT/api/gpu/detailed` should return HTTP 200 with a single  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
