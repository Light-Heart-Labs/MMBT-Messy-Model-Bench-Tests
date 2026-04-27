# PR #1018 Summary

**Title:** test(dream-cli): BATS regression shield for 5 dream-cli / supporting behaviors
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 16
**Lines changed:** 1436 (+1319/-117)
**Subsystems:** other, extensions, tests, scripts, dream-cli
**Labels:** None

## What the PR does

## ⚠️ Draft — depends on 5 upstream PRs merging first

Each test file pins behavior introduced by a different unmerged PR. Merge order below:

| Test file | Pins behavior from |
|---|---|
| `test-config-masking.bats` | #994 — `_cmd_config_is_secret` + schema cache |
| `test-compose-summary-wrapper.b

## Files touched

- dream-server/.env.schema.json
- dream-server/dream-cli
- dream-server/extensions/services/dashboard-api/routers/setup.py
- dream-server/extensions/services/dashboard/src/components/SetupWizard.jsx
- dream-server/extensions/services/dashboard/src/components/TemplatePicker.jsx
- dream-server/extensions/services/dashboard/src/lib/templates.js
- dream-server/extensions/services/dashboard/src/pages/Extensions.jsx
- dream-server/lib/service-registry.sh
- dream-server/scripts/dream-test-functional.sh
- dream-server/scripts/validate-env.sh
- dream-server/tests/bats-tests/test-compose-summary-wrapper.bats
- dream-server/tests/bats-tests/test-config-masking.bats
- dream-server/tests/bats-tests/test-dream-cli-flags.bats
- dream-server/tests/bats-tests/test-functional-resilience.bats
- dream-server/tests/bats-tests/test-sr-resolve.bats
- dream-server/tests/test-validate-env.sh

