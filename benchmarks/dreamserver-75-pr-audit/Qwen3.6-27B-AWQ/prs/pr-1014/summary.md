# PR #1014 Summary

**Title:** fix(tests): repair extension summary assertion in doctor diagnostics test
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 1
**Lines changed:** 3 (+2/-1)
**Subsystems:** tests
**Labels:** None

## What the PR does

## What
Replaces the order-dependent regex in `tests/test-doctor-extension-diagnostics.sh` test #9 ("Extension summary output present") with two order-independent chained greps.

## Why
The existing assertion
```bash
grep -q "ext_total.*ext_healthy" "$ROOT_DIR/scripts/dream-doctor.sh"
```
requires `

## Files touched

- dream-server/tests/test-doctor-extension-diagnostics.sh

