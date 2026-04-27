# PR #973 Summary

**Title:** docs: sync documentation with codebase after 50+ merged PRs
**Author:** yasinBursali
**Created:** 2026-04-16
**Files changed:** 23
**Lines changed:** 1209 (+477/-732)
**Subsystems:** other, extensions, tests, scripts, windows, docs
**Labels:** None

## What the PR does

## Summary

Systematic audit of the last 50 merged PRs against all existing documentation revealed stale, contradictory, and missing docs. This PR fixes them:

- **WINDOWS-QUICKSTART.md**: Remove "Coming Soon — Preflight Checks Only" language (Windows has been fully supported since March 2026). Add 

## Files touched

- README.md
- dream-server/.env.example
- dream-server/QUICKSTART.md
- dream-server/README.md
- dream-server/SECURITY.md
- dream-server/docs/FAQ.md
- dream-server/docs/HOST-AGENT-API.md
- dream-server/docs/MODE-SWITCH.md
- dream-server/docs/POST-INSTALL-CHECKLIST.md
- dream-server/docs/SUPPORT-MATRIX.md
- dream-server/docs/WINDOWS-QUICKSTART.md
- dream-server/extensions/CATALOG.md
- dream-server/extensions/services/langfuse/README.md
- dream-server/installers/windows/dream.ps1
- dream-server/installers/windows/install-windows.ps1
- dream-server/installers/windows/lib/install-report.ps1
- dream-server/installers/windows/lib/llm-endpoint.ps1
- dream-server/installers/windows/lib/opencode-config.ps1
- dream-server/installers/windows/phases/07-devtools.ps1
- dream-server/scripts/bootstrap-upgrade.sh

... and 3 more
