# PR #1025 Summary

## Claim In Plain English

fix(dashboard-api): wire Apple Silicon into /api/gpu/detailed

## Audit Restatement

Apple Silicon `/api/gpu/detailed` wiring is clean. `pytest tests/test_gpu_detailed.py -k "not history"` passes 19/19, and the Apple aggregate-to-single-card mapping is constrained to `GPU_BACKEND=apple`.

## Metadata

- Author: @yasinBursali
- Draft: False
- Base branch: main
- Head branch: fix/gpu-detailed-apple-silicon
- Changed files: 2
- Additions/deletions: +100 / -0
- Labels: none
