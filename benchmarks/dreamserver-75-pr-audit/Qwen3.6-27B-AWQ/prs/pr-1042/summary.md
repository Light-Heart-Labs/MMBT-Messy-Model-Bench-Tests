# PR #1042 Summary

**Title:** feat(support): add redacted diagnostics bundle generator
**Author:** boffin-dmytro
**Created:** 2026-04-25
**Files changed:** 3
**Lines changed:** 796 (+796/-0)
**Subsystems:** tests, other, scripts
**Labels:** None

## What the PR does

## Summary

This adds a standalone support bundle generator for DreamServer.

The new `scripts/dream-support-bundle.sh` command creates a redacted `.tar.gz` bundle under `artifacts/support/` so users can share one consistent diagnostics package when installs, Docker, GPU detection, extension sta

## Files touched

- dream-server/docs/SUPPORT-BUNDLE.md
- dream-server/scripts/dream-support-bundle.sh
- dream-server/tests/test-support-bundle.sh

