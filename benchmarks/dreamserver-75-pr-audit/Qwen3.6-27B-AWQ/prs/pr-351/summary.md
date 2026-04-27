# PR #351 Summary

**Title:** test: add comprehensive input validation and injection resistance tests
**Author:** reo0603
**Created:** 2026-03-17
**Files changed:** 864
**Lines changed:** 158041 (+10404/-147637)
**Subsystems:** other, extensions, macos, host-agent, tests, ci, compose, installer, scripts, installer-tests, resources, installer-windows, gpu, dream-cli, windows, docs
**Labels:** None

## What the PR does

## Summary

Adds 31 new security-focused tests validating that the dashboard API properly rejects malicious input patterns including SQL injection, command injection, path traversal, and encoding bypasses.

This PR is **test-only** with zero production code changes — purely defensive validation of e

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
