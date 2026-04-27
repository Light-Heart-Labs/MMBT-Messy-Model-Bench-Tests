# PR #1008 Summary

**Title:** refactor(dream-cli): guard .env grep pipelines against pipefail kill on missing keys
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 14 (+7/-7)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What
Seven `grep "^KEY=" .env | cut | tr` pipelines in `dream-cli` would
exit 1 when the key is absent. Under `set -eo pipefail` those
pipelines would kill the script before the downstream defensive
checks (`[[ -n ... ]]`, `${var:-(not set)}`) can handle the
empty-on-miss case the surrounding cod

## Files touched

- dream-server/dream-cli

