# PR #996 Summary

**Title:** fix(windows): generate DREAM_AGENT_KEY in installer env-generator.ps1
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 4
**Lines changed:** 12 (+7/-5)
**Subsystems:** windows
**Labels:** None

## What the PR does

## What

Windows installer now generates a dedicated `DREAM_AGENT_KEY` via `[System.Security.Cryptography.RandomNumberGenerator]`, writes it to `.env`, and exposes it via the `$envResult` hashtable. Removes the vestigial `DashboardKey` field from the return hashtable (zero readers anywhere in the in

## Files touched

- dream-server/installers/windows/install-windows.ps1
- dream-server/installers/windows/lib/env-generator.ps1
- dream-server/installers/windows/phases/06-directories.ps1
- dream-server/installers/windows/phases/07-devtools.ps1

