# PR #993 Summary

**Title:** fix(dream-cli): color-escape + table-separator + NO_COLOR spec
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 72 (+56/-16)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What

Three visual-polish fixes for `dream-cli`:

1. ANSI-C quoting (`$'\033[...'`) for color variables + `TTY && NO_COLOR`-guarded color emission, so color codes don't leak as literal escape text into non-ANSI-processing contexts (notably `cmd_help`'s heredoc, and piped/redirected output).
2. Ta

## Files touched

- dream-server/dream-cli

