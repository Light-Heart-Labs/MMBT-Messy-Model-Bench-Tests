# PR #999 Summary

**Title:** feat(dream-cli): Apple Silicon coverage for gpu subcommands and doctor
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 2
**Lines changed:** 84 (+79/-5)
**Subsystems:** scripts, dream-cli
**Labels:** None

## What the PR does

## What

`dream gpu` subcommands and `dream status --json` produce intent-appropriate output on Apple Silicon macOS instead of generic "nvidia-smi not found" warnings or return paths that treat an integrated GPU as a misconfiguration. `dream doctor` correctly reads RAM via `sysctl` (not `/proc/memin

## Files touched

- dream-server/dream-cli
- dream-server/scripts/dream-doctor.sh

