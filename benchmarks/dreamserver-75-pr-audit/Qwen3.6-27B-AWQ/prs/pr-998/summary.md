# PR #998 Summary

**Title:** fix(dream-cli): pipefail + surface LLM failures + exit-code contract
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 59 (+44/-15)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What

Three independent error-discipline improvements to `dream-cli`:

1. Promote shell options from `set -e` to `set -eo pipefail`, aligning with CLAUDE.md's project standard. Audit `| head -1` sites (converted to `| sed -n 1p` for SIGPIPE-safety).
2. `dream chat` and `dream benchmark` now actua

## Files touched

- dream-server/dream-cli

