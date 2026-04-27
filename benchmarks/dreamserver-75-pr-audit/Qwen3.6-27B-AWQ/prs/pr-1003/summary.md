# PR #1003 Summary

**Title:** fix(dashboard,dashboard-api): sentinel-based setup wizard success detection
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 6
**Lines changed:** 272 (+215/-57)
**Subsystems:** scripts, extensions
**Labels:** None

## What the PR does

## What

Three substantive fixes for the dashboard's Setup Wizard, plus correctness fixes for the diagnostic shell script:

1. **Machine-readable `__DREAM_RESULT__:PASS|FAIL:<rc>` sentinel** on `/api/setup/test` (both `run_tests` happy path and `error_stream` fallback). The wizard no longer greenlig

## Files touched

- dream-server/extensions/services/dashboard-api/routers/setup.py
- dream-server/extensions/services/dashboard/src/components/SetupWizard.jsx
- dream-server/extensions/services/dashboard/src/components/TemplatePicker.jsx
- dream-server/extensions/services/dashboard/src/lib/templates.js
- dream-server/extensions/services/dashboard/src/pages/Extensions.jsx
- dream-server/scripts/dream-test-functional.sh

