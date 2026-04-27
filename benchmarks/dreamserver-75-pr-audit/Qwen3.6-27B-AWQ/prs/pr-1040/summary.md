# PR #1040 Summary

**Title:** fix(langfuse): chown postgres/clickhouse data dirs to image uids on Linux
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 5
**Lines changed:** 476 (+473/-3)
**Subsystems:** host-agent, tests, extensions
**Labels:** None

## What the PR does

> **DRAFT: must merge AFTER #1030.** This branch is based on `fix/host-agent-install-flow` (#1030) and depends on `_find_ext_dir` for built-in hook discovery. Promote to ready-for-review after #1030 merges.

## Summary
langfuse's `postgres:17.9-alpine` (uid **70**) and `clickhouse/clickhouse-server:

## Files touched

- dream-server/bin/dream-host-agent.py
- dream-server/extensions/services/dashboard-api/tests/test_host_agent.py
- dream-server/extensions/services/langfuse/hooks/post_install.sh
- dream-server/extensions/services/langfuse/manifest.yaml
- dream-server/tests/reproducers/langfuse-uid-check.sh

