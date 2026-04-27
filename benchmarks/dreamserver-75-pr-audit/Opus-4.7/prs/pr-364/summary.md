# PR #364 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> feat(dashboard-api): add settings, voice runtime, and diagnostics APIs

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary
This PR adds the missing runtime API contracts used by Dashboard setup/success/voice flows, and backs them with persistence + tests.

## Why
Several frontend and integration flows depend on endpoints that were absent in `dashboard-api` (`/api/settings`, `/api/voice/*`, `/api/test/*`). This created broken UX paths and false-negative health/feature checks.

## What Changed
- Added new runtime router:
  - `GET /api/settings`
  - `GET /api/voice/settings`
  - `POST /api/voice/settings`
  - `GET /api/voice/status`
  - `POST /api/voice/token`
  - `GET /api/test/{llm|voice|rag|workflows}`
- Wired runtime router into FastAPI app bootstrap.
- Added tests for:
  - settings payload shape/dynamic fields
  - voice settings default + persistence roundtrip
  - voice status aggregation behavior
  - voice token credential checks + JWT format
  - diagnostics endpoint behavior + unknown-target handling
- Updated `dashboard-api` README endpoint docs.

## Implementation Notes
- Voice settings persist to `DATA_DIR/config/voice-settings.json`.
- LiveKit token is minted with HS256 using `LIVEKIT_API_KEY` + `LIVEKIT_API_SECRET`.
- Voice status aggregates health for Whisper, TTS, and LiveKit with an `available` summary boolean.
- Diagnostics endpoints are intentionally lightweight and UI-friendly.

## Testing
- Added/updated unit tests in `tests/test_routers.py`.
- Static compile check passed via `python3 -m py_compile`.
- Full pytest run was not possible in   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
