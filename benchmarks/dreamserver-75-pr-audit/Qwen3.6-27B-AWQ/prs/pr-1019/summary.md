# PR #1019 Summary

**Title:** test+fix(setup): complete __DREAM_RESULT__ sentinel contract (exception path + tests)
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 9
**Lines changed:** 749 (+689/-60)
**Subsystems:** scripts, extensions
**Labels:** None

## What the PR does

## ⚠️ Draft — depends on #1003 merging first

#1003 (`fix/dashboard-setup-wizard`) introduces the `__DREAM_RESULT__:PASS|FAIL:<rc>` sentinel parser in `SetupWizard.jsx` and the emitter for the happy-path + error-stream branches. This PR completes the contract by adding the emitter for the **exceptio

## Files touched

- dream-server/extensions/services/dashboard-api/routers/setup.py
- dream-server/extensions/services/dashboard-api/tests/test_setup_sentinel.py
- dream-server/extensions/services/dashboard/src/components/SetupWizard.jsx
- dream-server/extensions/services/dashboard/src/components/TemplatePicker.jsx
- dream-server/extensions/services/dashboard/src/components/__tests__/SetupWizard.test.jsx
- dream-server/extensions/services/dashboard/src/components/__tests__/TemplatePicker.a11y.test.jsx
- dream-server/extensions/services/dashboard/src/lib/templates.js
- dream-server/extensions/services/dashboard/src/pages/Extensions.jsx
- dream-server/scripts/dream-test-functional.sh

