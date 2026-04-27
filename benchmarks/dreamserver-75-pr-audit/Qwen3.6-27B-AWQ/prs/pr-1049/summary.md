# PR #1049 Summary

**Title:** fix(jupyter): convert command to exec-form list to avoid shell splitting
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 1
**Lines changed:** 10 (+9/-1)
**Subsystems:** resources
**Labels:** None

## What the PR does

## What
Convert the jupyter community extension's `command:` from shell-form scalar to YAML list (exec-form) in `resources/dev/extensions-library/services/jupyter/compose.yaml`.

## Why
Defensive hardening. The previous `command:` was a single shell-form string:
```yaml
command: start.sh jupyter lab

## Files touched

- resources/dev/extensions-library/services/jupyter/compose.yaml

