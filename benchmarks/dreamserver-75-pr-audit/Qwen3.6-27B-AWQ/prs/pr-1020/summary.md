# PR #1020 Summary

**Title:** test: contract + mock coverage for Apple Silicon GPU backends
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 4
**Lines changed:** 543 (+538/-5)
**Subsystems:** scripts, dream-cli, tests
**Labels:** None

## What the PR does

## ⚠️ Draft — depends on #999 merging first

#999 (`fix/dream-cli-apple-silicon-coverage`) introduces the 5 Apple `GPU_BACKEND=apple` code paths (`_gpu_status`, `_gpu_topology`, `_gpu_validate`, `_gpu_reassign`, `cmd_status_json`) plus a Darwin branch in `scripts/dream-doctor.sh` (RAM via `sysctl hw

## Files touched

- dream-server/dream-cli
- dream-server/scripts/dream-doctor.sh
- dream-server/tests/contracts/test-dream-doctor.sh
- dream-server/tests/test-gpu-apple.sh

