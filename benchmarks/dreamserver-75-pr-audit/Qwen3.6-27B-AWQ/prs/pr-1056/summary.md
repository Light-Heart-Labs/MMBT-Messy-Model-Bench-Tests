# PR #1056 Summary

**Title:** fix(dashboard-api): catalog timeout, orphaned whitelist, GPU passthrough scan, health_port
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 4
**Lines changed:** 150 (+138/-12)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## What
Four scoped fixes to the dashboard-api extension paths, plus three new unit tests covering the new compose-scan rule.

- **#A — Catalog/detail health-fan-out timeout:** add a separate short timeout (5 s) for the catalog and \`extension_detail\` user-extension health probes, distinct from the

## Files touched

- dream-server/extensions/services/dashboard-api/helpers.py
- dream-server/extensions/services/dashboard-api/routers/extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_extensions.py
- dream-server/extensions/services/dashboard-api/user_extensions.py

