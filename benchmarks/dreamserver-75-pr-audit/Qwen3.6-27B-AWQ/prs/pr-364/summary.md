# PR #364 Summary

**Title:** feat(dashboard-api): add settings, voice runtime, and diagnostics APIs
**Author:** championVisionAI
**Created:** 2026-03-18
**Files changed:** 864
**Lines changed:** 157995 (+10550/-147445)
**Subsystems:** other, extensions, macos, host-agent, tests, ci, compose, installer, scripts, installer-tests, resources, installer-windows, gpu, dream-cli, windows, docs
**Labels:** None

## What the PR does

## Summary
This PR adds the missing runtime API contracts used by Dashboard setup/success/voice flows, and backs them with persistence + tests.

## Why
Several frontend and integration flows depend on endpoints that were absent in `dashboard-api` (`/api/settings`, `/api/voice/*`, `/api/test/*`).

## Files touched

- .claude/commands/tdd.md
- .github/dependabot.yml
- .github/prompts/issue-to-pr.md
- .github/prompts/nightly-code-review.md
- .github/prompts/nightly-docs-update.md
- .github/scripts/anthropic_helper.py
- .github/scripts/apply-docstrings.py
- .github/scripts/apply-type-hints.py
- .github/scripts/generate-docstrings.py
- .github/scripts/generate-type-hints.py
- .github/test-events/issue-opened.json
- .github/test-events/pr-opened.json
- .github/test-events/release-created.json
- .github/workflows/ai-issue-triage.yml
- .github/workflows/autonomous-code-scanner.yml
- .github/workflows/build-dreamforge.yml
- .github/workflows/claude-review.yml
- .github/workflows/dashboard.yml
- .github/workflows/issue-to-pr.yml
- .github/workflows/lint-powershell.yml

... and 844 more
