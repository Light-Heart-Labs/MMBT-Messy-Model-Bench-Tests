# PR #1000 Summary

**Title:** feat(dream-cli): --json flag on list/status and document doctor --json
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 59 (+53/-6)
**Subsystems:** dream-cli
**Labels:** None

## What the PR does

## What

`dream list --json` and `dream status --json` now work as advertised. Previously the `--json` flag was silently dropped because the main case dispatch forwarded no arguments to the subcommands. Also documents the previously-undocumented `dream doctor --json`, keeps `dream status-json` as a 

## Files touched

- dream-server/dream-cli

