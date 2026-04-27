# PR #966 Summary

**Title:** docs(platform): sync Windows and macOS support docs
**Author:** boffin-dmytro
**Created:** 2026-04-15
**Files changed:** 70
**Lines changed:** 4568 (+599/-3969)
**Subsystems:** other, extensions, macos, host-agent, tests, ci, compose, installer, scripts, dream-cli, windows
**Labels:** None

## What the PR does

## Summary

This cleans up the remaining Windows/macOS support doc contradictions in the shipped user-facing docs.

The main mismatch before this change was that the root README and support matrix described Windows as supported today, while the Windows quickstart still described a preflight-only fut

## Files touched

- .github/workflows/ai-issue-triage.yml
- .github/workflows/autonomous-code-scanner.yml
- .github/workflows/build-dreamforge.yml
- .github/workflows/claude-review.yml
- .github/workflows/dashboard.yml
- .github/workflows/issue-to-pr.yml
- .github/workflows/lint-python.yml
- .github/workflows/nightly-code-review.yml
- .github/workflows/nightly-docs-update.yml
- .github/workflows/release-notes.yml
- .github/workflows/type-check-python.yml
- .github/workflows/validate-catalog.yml
- dream-server/.env.example
- dream-server/.env.schema.json
- dream-server/bin/dream-host-agent.py
- dream-server/config/model-library.json
- dream-server/docker-compose.base.yml
- dream-server/docker-compose.local.yml
- dream-server/docs/WINDOWS-INSTALL-WALKTHROUGH.md
- dream-server/dream-cli

... and 50 more
