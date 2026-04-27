# PR #1050 Summary

**Title:** fix(installer): block non-POSIX INSTALL_DIR + verify Docker Desktop sharing
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 5
**Lines changed:** 352 (+351/-1)
**Subsystems:** macos, host-agent, other, windows
**Labels:** None

## What the PR does

## What
Block install on a non-POSIX-permission filesystem at `INSTALL_DIR` (security regression), and pre-verify Docker Desktop's file-sharing allowlist before any compose-up. Per-platform detection across all three installers, plus a defense-in-depth guard in the host agent.

## Why
**Bug #1 — non

## Files touched

- dream-server/bin/dream-host-agent.py
- dream-server/installers/macos/install-macos.sh
- dream-server/installers/macos/lib/preflight-fs.sh
- dream-server/installers/phases/01-preflight.sh
- dream-server/installers/windows/phases/01-preflight.ps1

