# PR #988 Summary

**Title:** fix(security): bind llama-server and host agent to loopback
**Author:** yasinBursali
**Created:** 2026-04-22
**Files changed:** 15
**Lines changed:** 784 (+148/-636)
**Subsystems:** other, macos, host-agent, tests, scripts, windows
**Labels:** None

## What the PR does

## What
Binds native `llama-server` (macOS + Windows) and the Linux host agent fallback to `127.0.0.1` (loopback) instead of `0.0.0.0` (all interfaces).

## Why
Native `llama-server` on macOS (Metal) and Windows (Lemonade + llama.cpp) previously listened on `0.0.0.0:8080`, making the LLM inference A

## Files touched

- dream-server/.env.example
- dream-server/.env.schema.json
- dream-server/bin/dream-host-agent.py
- dream-server/installers/macos/dream-macos.sh
- dream-server/installers/macos/install-macos.sh
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

