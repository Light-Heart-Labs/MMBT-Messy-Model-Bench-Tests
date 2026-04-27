# PR #983 Summary

**Title:** feat(resources): add p2p-gpu deploy toolkit for Vast.ai GPU instances
**Author:** Arifuzzamanjoy
**Created:** 2026-04-18
**Files changed:** 102
**Lines changed:** 9708 (+5609/-4099)
**Subsystems:** other, extensions, macos, host-agent, tests, ci, compose, installer, scripts, resources, dream-cli, windows
**Labels:** None

## What the PR does

### What

One-command DreamServer deployment on peer-to-peer GPU marketplaces (Vast.ai). Handles 28 known provider quirks — root user rejection, Docker socket permissions, NVIDIA/AMD toolkit setup, model bootstrapping, multi-GPU topology, reverse proxy, and SSH tunnel generation.

### Where

E

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
- .github/workflows/p2p-gpu.yml
- .github/workflows/release-notes.yml
- .github/workflows/type-check-python.yml
- .github/workflows/validate-catalog.yml
- .gitignore
- dream-server/.env.example
- dream-server/.env.schema.json
- dream-server/bin/dream-host-agent.py
- dream-server/config/model-library.json
- dream-server/docker-compose.base.yml
- dream-server/docker-compose.local.yml

... and 82 more
