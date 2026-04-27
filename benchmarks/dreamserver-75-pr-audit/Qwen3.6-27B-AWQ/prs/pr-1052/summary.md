# PR #1052 Summary

**Title:** test(langfuse): structural guard for setup_hook + hook file coexistence
**Author:** yasinBursali
**Created:** 2026-04-26
**Files changed:** 1
**Lines changed:** 34 (+34/-0)
**Subsystems:** extensions
**Labels:** None

## What the PR does

> **DRAFT: must merge AFTER #1040.** This PR's tests assert that langfuse's `service.setup_hook` and `hooks/post_install.sh` exist. Both are added by upstream PR #1040 (the langfuse postgres uid 70 install fix). Until #1040 merges, these tests fail on bare `upstream/main` — that's expected. Promote 

## Files touched

- dream-server/extensions/services/dashboard-api/tests/test_hooks.py

