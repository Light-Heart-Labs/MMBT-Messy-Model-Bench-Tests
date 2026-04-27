# PR #1010 Summary

**Title:** chore(schema): mark provider API keys as secret in .env.schema.json
**Author:** yasinBursali
**Created:** 2026-04-23
**Files changed:** 2
**Lines changed:** 44 (+39/-5)
**Subsystems:** other, extensions
**Labels:** None

## What the PR does

## What
Flip `"secret": true` on five provider API-key entries in `dream-server/.env.schema.json`:
- `TARGET_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `TOGETHER_API_KEY`
- `LIVEKIT_API_KEY`

Adds a parametric pytest locking the flag in as a regression guard.

## Why
These keys were already

## Files touched

- dream-server/.env.schema.json
- dream-server/extensions/services/dashboard-api/tests/test_settings_env.py

