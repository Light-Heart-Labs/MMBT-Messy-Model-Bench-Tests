# PR #1043 Summary

**Title:** fix(installer): custom menu's 'n' answers were not actually disabling services
**Author:** y-coffee-dev
**Created:** 2026-04-25
**Files changed:** 12
**Lines changed:** 814 (+148/-666)
**Subsystems:** other, tests, installer, scripts, windows
**Labels:** None

## What the PR does

Fixes two compounding bugs caused users in Custom mode to get almost every optional service installed regardless of their answers:

1. The prompt logic used '[[ $REPLY =~ ^[Nn]$ ]] || ENABLE_X=true', which only SET flags to true and never to false. Since install-core defaults were already true (VO

## Files touched

- dream-server/install-core.sh
- dream-server/installers/phases/03-features.sh
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

