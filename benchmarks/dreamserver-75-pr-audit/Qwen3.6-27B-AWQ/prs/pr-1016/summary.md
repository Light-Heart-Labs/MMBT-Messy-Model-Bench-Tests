# PR #1016 Summary

**Title:** fix(dream-cli): Apple GPU output polish + compose wrapper SIGINT/zero-match
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 3
**Lines changed:** 203 (+170/-33)
**Subsystems:** scripts, other, dream-cli
**Labels:** None

## What the PR does

## ⚠️ Draft — depends on #999 AND #1001 merging first

All four fixes live in code introduced by unmerged upstream PRs:
- **#401, #402** target the Apple GPU_BACKEND branches added by #999 (`fix/dream-cli-apple-silicon-coverage`)
- **#405, #407** target `_compose_run_with_summary` added by #1001 (`f

## Files touched

- dream-server/dream-cli
- dream-server/lib/service-registry.sh
- dream-server/scripts/dream-doctor.sh

