# PR #1011 Summary

**Title:** chore(bash32): guard declare -A callers + route dream-cli validate through $BASH
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 6
**Lines changed:** 46 (+43/-3)
**Subsystems:** scripts, other, dream-cli
**Labels:** None

## What the PR does

## What
Adds Bash 4+ guards to five scripts that use `declare -A` without one, and routes two `dream config validate` subprocesses through `"$BASH"` so they inherit dream-cli's modern bash interpreter.

Files touched (6):
- `dream-server/scripts/pre-download.sh` — Pattern A guard (bare `exit 1`)
- `

## Files touched

- dream-server/dream-cli
- dream-server/installers/phases/03-features.sh
- dream-server/lib/progress.sh
- dream-server/scripts/dream-test-functional.sh
- dream-server/scripts/pre-download.sh
- dream-server/scripts/validate-env.sh

