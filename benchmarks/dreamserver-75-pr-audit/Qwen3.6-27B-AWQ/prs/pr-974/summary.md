# PR #974 Summary

**Title:** fix(bootstrap): use $DOCKER_CMD for DreamForge restart
**Author:** yasinBursali
**Created:** 2026-04-17
**Files changed:** 10
**Lines changed:** 726 (+104/-622)
**Subsystems:** tests, scripts, windows
**Labels:** None

## What the PR does

## What
Use `$DOCKER_CMD` instead of bare `docker` for DreamForge restart in bootstrap-upgrade.sh.

## Why
Line 464 used bare `docker` while the rest of the file correctly uses `$DOCKER_CMD`. On Linux systems requiring sudo for Docker, the restart silently failed with a permission error absorbed by 

## Files touched

- dream-server/installers/windows/dream.ps1
- dream-server/installers/windows/install-windows.ps1
- dream-server/installers/windows/lib/install-report.ps1
- dream-server/installers/windows/lib/llm-endpoint.ps1
- dream-server/installers/windows/lib/opencode-config.ps1
- dream-server/installers/windows/phases/07-devtools.ps1
- dream-server/scripts/bootstrap-upgrade.sh
- dream-server/scripts/update-windows-opencode-config.ps1
- dream-server/tests/test-windows-opencode-config.sh
- dream-server/tests/test-windows-report-command.sh

