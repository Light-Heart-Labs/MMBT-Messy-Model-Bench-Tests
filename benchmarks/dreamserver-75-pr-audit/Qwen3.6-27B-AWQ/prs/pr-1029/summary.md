# PR #1029 Summary

**Title:** fix(resolver): dedupe override.yml; apply gpu_backends filter to user-extensions
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 2
**Lines changed:** 53 (+46/-7)
**Subsystems:** compose, scripts
**Labels:** None

## What the PR does

## What
Two resolver fixes bundled:
1. Stop appending `docker-compose.override.yml` twice to `COMPOSE_FLAGS`.
2. Apply the same `gpu_backends` filter to user-installed extensions that built-in extensions already receive.

## Why
**Defect 1:** `installers/lib/compose-select.sh` called the resolver (w

## Files touched

- dream-server/installers/lib/compose-select.sh
- dream-server/scripts/resolve-compose-stack.sh

