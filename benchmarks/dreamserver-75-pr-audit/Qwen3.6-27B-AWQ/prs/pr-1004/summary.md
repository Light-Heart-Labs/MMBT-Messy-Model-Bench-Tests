# PR #1004 Summary

**Title:** fix(resolver): skip compose.local.yaml on Apple Silicon to avoid llama-server deadlock
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 9 (+7/-2)
**Subsystems:** scripts
**Labels:** None

## What the PR does

## What
`scripts/resolve-compose-stack.sh` was unconditionally including extension
`compose.local.yaml` overlays whenever `DREAM_MODE` was `local`, `hybrid`,
or `lemonade` — even when `gpu_backend` was `apple`. On macOS, those
overlays deadlock the stack.

## Why
Extension `compose.local.yaml` overl

## Files touched

- dream-server/scripts/resolve-compose-stack.sh

