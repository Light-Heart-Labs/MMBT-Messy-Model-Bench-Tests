# PR #1037 Summary

**Title:** fix(dashboard): expandable error text + poll recovery on extensions page
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 3
**Lines changed:** 206 (+191/-15)
**Subsystems:** extensions
**Labels:** None

## What the PR does

> **DRAFT: must merge AFTER #1031.** This branch is based on `fix/progress-state-machine` (#1031); commits shown here will reduce to just this PR's delta once #1031 lands. Promote to ready-for-review after #1031 merges.

## Summary
Two defects in `Extensions.jsx`:
1. Error messages on extension card

## Files touched

- dream-server/extensions/services/dashboard-api/routers/extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_extensions.py
- dream-server/extensions/services/dashboard/src/pages/Extensions.jsx

