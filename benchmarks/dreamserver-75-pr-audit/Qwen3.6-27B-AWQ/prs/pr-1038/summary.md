# PR #1038 Summary

**Title:** fix(dashboard-api): honor pre_start return, surface post_start failure
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 3
**Lines changed:** 248 (+240/-8)
**Subsystems:** extensions
**Labels:** None

## What the PR does

> **DRAFT: must merge AFTER #1031.** This branch is based on `fix/progress-state-machine` (#1031) and depends on `_write_error_progress` introduced there. Promote to ready-for-review after #1031 merges.

## Summary
`enable_extension` silently discarded the return value of `_call_agent_hook("pre_star

## Files touched

- dream-server/extensions/services/dashboard-api/routers/extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_extensions.py
- dream-server/extensions/services/dashboard/src/pages/Extensions.jsx

