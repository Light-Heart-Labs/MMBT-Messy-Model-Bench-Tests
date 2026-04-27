# PR #1039 Summary

**Title:** fix(host-agent): retry install failure through the hook + progress path
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 3
**Lines changed:** 533 (+528/-5)
**Subsystems:** host-agent, extensions
**Labels:** None

## What the PR does

> **DRAFT: must merge AFTER #1030.** This branch is based on `fix/host-agent-install-flow` (#1030) and depends on `_find_ext_dir` for built-in hook discovery. Promote to ready-for-review after #1030 merges.

## Summary
Clicking **Enable** on an extension whose install left `{"status":"error"}` in it

## Files touched

- dream-server/bin/dream-host-agent.py
- dream-server/extensions/services/dashboard-api/routers/extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_host_agent.py

