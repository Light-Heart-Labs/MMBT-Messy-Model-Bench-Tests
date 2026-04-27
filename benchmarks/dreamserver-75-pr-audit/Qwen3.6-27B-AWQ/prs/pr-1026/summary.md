# PR #1026 Summary

**Title:** fix(installer): pre-mark setup wizard complete on successful install
**Author:** yasinBursali
**Created:** 2026-04-24
**Files changed:** 4
**Lines changed:** 63 (+63/-0)
**Subsystems:** macos, tests, other, windows
**Labels:** None

## What the PR does

## What
All three installers now write `setup-complete.json` after a successful install, so the setup wizard does not reappear on first dashboard load.

## Why
`routers/setup.py::setup_status` returns `first_run=true` whenever `${SETUP_CONFIG_DIR}/setup-complete.json` is absent. The file was only ev

## Files touched

- dream-server/installers/macos/install-macos.sh
- dream-server/installers/phases/13-summary.sh
- dream-server/installers/windows/install-windows.ps1
- dream-server/tests/contracts/test-installer-contracts.sh

