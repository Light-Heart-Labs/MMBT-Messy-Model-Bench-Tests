# PR #1022 Summary

**Title:** fix(dashboard-api): async hygiene in routers/extensions.py
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 2
**Lines changed:** 114 (+102/-12)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## What
Fixes three async-hygiene defects in `routers/extensions.py`: blocking urllib calls on the event-loop thread, over-broad `except Exception` catches that swallow programmer errors, and a fire-and-forget executor future that silently discards cleanup failures.

## Why
- `extension_logs` and `e

## Files touched

- dream-server/extensions/services/dashboard-api/routers/extensions.py
- dream-server/extensions/services/dashboard-api/tests/test_extensions.py

