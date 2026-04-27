# PR #1025 Diff Analysis

## Claimed Change

fix(dashboard-api): wire Apple Silicon into /api/gpu/detailed

## Actual Change Characterization

Apple Silicon `/api/gpu/detailed` wiring is clean. `pytest tests/test_gpu_detailed.py -k "not history"` passes 19/19, and the Apple aggregate-to-single-card mapping is constrained to `GPU_BACKEND=apple`.

## Surface Area

- Subsystems: dashboard-api, dashboard, gpu/amd
- Changed files: 2
- Additions/deletions: +100 / -0

## Fit Assessment

The change is small or well-contained enough for merge after CI.
