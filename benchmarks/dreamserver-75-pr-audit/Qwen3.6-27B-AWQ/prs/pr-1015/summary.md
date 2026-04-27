# PR #1015 Summary

**Title:** fix(dashboard): template picker defensive fixes (handleApply + vacuous-truth)
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 6
**Lines changed:** 275 (+217/-58)
**Subsystems:** scripts, extensions
**Labels:** None

## What the PR does

## ⚠️ Draft — depends on #1003 merging first

This PR is stacked on `fix/dashboard-setup-wizard` (#1003) because `lib/templates.js` (the target of the #409 fix) doesn't exist on `upstream/main` yet — it's created by #1003. Once #1003 merges, I'll rebase on `main` and the PR diff will collapse to exa

## Files touched

- dream-server/extensions/services/dashboard-api/routers/setup.py
- dream-server/extensions/services/dashboard/src/components/SetupWizard.jsx
- dream-server/extensions/services/dashboard/src/components/TemplatePicker.jsx
- dream-server/extensions/services/dashboard/src/lib/templates.js
- dream-server/extensions/services/dashboard/src/pages/Extensions.jsx
- dream-server/scripts/dream-test-functional.sh

