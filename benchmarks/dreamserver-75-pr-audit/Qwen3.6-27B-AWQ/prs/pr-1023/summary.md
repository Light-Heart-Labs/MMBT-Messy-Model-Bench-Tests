# PR #1023 Summary

**Title:** fix(scripts): SIGPIPE-safe first-line selection in 5 scripts
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 5
**Lines changed:** 12 (+6/-6)
**Subsystems:** macos, scripts
**Labels:** None

## What the PR does

## What
Replace `| head -1 |` / `| head -n 1 |` with `| sed -n '1p' |` in five scripts to eliminate SIGPIPE termination under `set -euo pipefail`.

## Why
`head -1` closes its stdin after consuming one line. When the upstream pipeline stage produces multiple lines (multi-GPU nvidia-smi output, multi

## Files touched

- dream-server/installers/macos/dream-macos.sh
- dream-server/installers/macos/lib/env-generator.sh
- dream-server/scripts/check-offline-models.sh
- dream-server/scripts/dream-preflight.sh
- dream-server/scripts/pre-download.sh

