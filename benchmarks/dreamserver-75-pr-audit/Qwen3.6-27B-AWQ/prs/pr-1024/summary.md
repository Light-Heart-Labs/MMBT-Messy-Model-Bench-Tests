# PR #1024 Summary

**Title:** refactor(scripts): array-expand COMPOSE_FLAGS for SC2086 + glob safety
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 3
**Lines changed:** 39 (+31/-8)
**Subsystems:** scripts
**Labels:** None

## What the PR does

## What
Convert `$COMPOSE_FLAGS` (and `$ENV_FILE_FLAG`) from unquoted string expansion to bash array expansion in three operational scripts: `validate.sh`, `dream-preflight.sh`, and `validate-compose-stack.sh`.

## Why
All three scripts passed `$COMPOSE_FLAGS` unquoted to `docker compose`, producing

## Files touched

- dream-server/scripts/dream-preflight.sh
- dream-server/scripts/validate-compose-stack.sh
- dream-server/scripts/validate.sh

