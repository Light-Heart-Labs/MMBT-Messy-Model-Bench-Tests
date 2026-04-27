# PR #1033 Summary

**Title:** fix(extensions): align librechat MONGO_URI guard; remove :? from jupyter command
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 2
**Lines changed:** 4 (+2/-2)
**Subsystems:** resources
**Labels:** None

## What the PR does

## What
Two one-line fixes to community extension `:?` interpolation guards.

## Why
- **librechat** asymmetry: the `librechat-mongodb` service uses `${LIBRECHAT_MONGO_PASSWORD:?}` at initdb, enforcing a real password. But the `librechat` service's `MONGO_URI` interpolated the same variable without 

## Files touched

- resources/dev/extensions-library/services/jupyter/compose.yaml
- resources/dev/extensions-library/services/librechat/compose.yaml

