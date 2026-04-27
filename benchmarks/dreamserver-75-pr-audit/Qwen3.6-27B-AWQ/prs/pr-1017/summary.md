# PR #1017 Summary

**Title:** docs(security): Linux host-agent fallback is 127.0.0.1 post-#988
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 20
**Lines changed:** 523 (+393/-130)
**Subsystems:** other, extensions, macos, host-agent, scripts, windows, docs
**Labels:** None

## What the PR does

## ⚠️ Draft — depends on #988 AND #973 merging first

- **#988** (`fix/security-loopback`) changes the Linux Docker-bridge-gateway detection fallback in `bin/dream-host-agent.py` from `0.0.0.0` to `127.0.0.1`.
- **#973** (`docs/sync-documentation-with-codebase`) introduces the "Host Agent Network Bi

## Files touched

- README.md
- dream-server/.env.example
- dream-server/.env.schema.json
- dream-server/QUICKSTART.md
- dream-server/README.md
- dream-server/SECURITY.md
- dream-server/bin/dream-host-agent.py
- dream-server/docs/FAQ.md
- dream-server/docs/HOST-AGENT-API.md
- dream-server/docs/MODE-SWITCH.md
- dream-server/docs/POST-INSTALL-CHECKLIST.md
- dream-server/docs/SUPPORT-MATRIX.md
- dream-server/docs/WINDOWS-QUICKSTART.md
- dream-server/extensions/CATALOG.md
- dream-server/extensions/services/langfuse/README.md
- dream-server/installers/macos/dream-macos.sh
- dream-server/installers/macos/install-macos.sh
- dream-server/installers/windows/dream.ps1
- dream-server/installers/windows/install-windows.ps1
- dream-server/scripts/bootstrap-upgrade.sh

