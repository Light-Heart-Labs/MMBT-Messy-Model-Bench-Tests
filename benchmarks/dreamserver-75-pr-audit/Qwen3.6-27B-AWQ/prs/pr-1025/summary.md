# PR #1025 Summary

**Title:** fix(dashboard-api): wire Apple Silicon into /api/gpu/detailed
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 2
**Lines changed:** 100 (+100/-0)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## What
Wire Apple Silicon GPU detection into `/api/gpu/detailed` so the endpoint returns real data instead of a 503 on macOS.

## Why
`_get_raw_gpus` in `routers/gpu.py` only had a branch for `amd`, then fell through to NVIDIA/AMD sysfs probing — both return `None` on macOS, yielding an empty list.

## Files touched

- dream-server/extensions/services/dashboard-api/routers/gpu.py
- dream-server/extensions/services/dashboard-api/tests/test_gpu_detailed.py

