# PR #1013 Summary

**Title:** fix(dream-agent-key): complete DREAM_AGENT_KEY lifecycle on macOS + docs
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 2
**Lines changed:** 8 (+8/-0)
**Subsystems:** macos, other
**Labels:** None

## What the PR does

## What
Two related gaps in the `DREAM_AGENT_KEY` lifecycle (the independent 32-byte hex secret introduced by PR #979):

1. **`.env.example`** — adds a commented documentation entry for `DREAM_AGENT_KEY` next to the existing `DASHBOARD_API_KEY` entry, with a generation hint and a warning that rotati

## Files touched

- dream-server/.env.example
- dream-server/installers/macos/lib/env-generator.sh

