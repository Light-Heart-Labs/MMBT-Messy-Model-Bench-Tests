# PR #1005 Summary

**Title:** fix(macos): install-time polish — DIM constant, busybox pin, healthcheck rewrite
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 3
**Lines changed:** 52 (+35/-17)
**Subsystems:** macos
**Labels:** None

## What the PR does

## What
Three macOS-only install-time defects, each in a distinct file.

## Why / How

### 1. `DIM` color variable missing from macOS constants
`installers/macos/lib/ui.sh:180` referenced `\${DIM}` in the final
summary banner, but the macOS `lib/constants.sh` did not define it
(the shared `installer

## Files touched

- dream-server/installers/macos/docker-compose.macos.yml
- dream-server/installers/macos/install-macos.sh
- dream-server/installers/macos/lib/constants.sh

