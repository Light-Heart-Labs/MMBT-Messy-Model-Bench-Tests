# PR #1012 Summary

**Title:** refactor(windows): trim dead fields from New-DreamEnv return hash
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 4
**Lines changed:** 10 (+3/-7)
**Subsystems:** windows
**Labels:** None

## What the PR does

## What
Reduces the `$envResult` hashtable returned by `New-DreamEnv` from four fields (`EnvPath`, `SearxngSecret`, `OpenclawToken`, `DashboardKey`) to the two that are actually consumed (`SearxngSecret`, `OpenclawToken`). Updates three stale header comments and the dry-run stub to match.

Files tou

## Files touched

- dream-server/installers/windows/install-windows.ps1
- dream-server/installers/windows/lib/env-generator.ps1
- dream-server/installers/windows/phases/06-directories.ps1
- dream-server/installers/windows/phases/07-devtools.ps1

