# PR #994 Summary

**Title:** fix(dream-cli): schema-driven secret masking + macOS Bash 4 validation
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 4
**Lines changed:** 104 (+89/-15)
**Subsystems:** scripts, other, dream-cli, tests
**Labels:** None

## What the PR does

## What

Four related hardenings to `dream config` and its helpers:

1. **Schema-driven masking in `dream config show`** — replace the narrow keyword regex (which missed `_PASSWORD`, `_SALT`, `_PASS` suffixed fields) with `.env.schema.json`-driven detection.
2. **Bash 4+ invocation** — `dream config

## Files touched

- dream-server/.env.schema.json
- dream-server/dream-cli
- dream-server/scripts/validate-env.sh
- dream-server/tests/test-validate-env.sh

