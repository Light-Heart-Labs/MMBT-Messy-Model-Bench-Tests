# PR #1054 Summary

**Title:** fix(dashboard-api): require deployable compose.yaml to mark extension installable
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 1
**Lines changed:** 5 (+4/-1)
**Subsystems:** extensions
**Labels:** None

## What the PR does

## What
Tighten `_is_installable` in `routers/extensions.py` so an extension is only advertised as installable when it actually has a deployable `compose.yaml` on disk.

## Why
The library currently ships three entries that have only `compose.yaml.disabled` or `compose.yaml.reference` files:

- `dif

## Files touched

- dream-server/extensions/services/dashboard-api/routers/extensions.py

