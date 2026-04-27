# PR #1010 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> chore(schema): mark provider API keys as secret in .env.schema.json

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Flip `"secret": true` on five provider API-key entries in `dream-server/.env.schema.json`:
- `TARGET_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `TOGETHER_API_KEY`
- `LIVEKIT_API_KEY`

Adds a parametric pytest locking the flag in as a regression guard.

## Why
These keys were already being masked in `dream config show` (inline grep on `key=`) and in the dashboard-api `GET /api/settings/env` response (via `_is_secret_field` regex fallback on `API_KEY`). The schema is the intended authoritative source, and relying on name-pattern coincidence is fragile — any future rename that breaks the pattern would silently stop masking.

No runtime behavior change: both the schema-authoritative path and the regex fallback produce the same masked output today. This just routes through the primary path.

## How
- Added `"secret": true` as the third property on each of the five entries, matching the style of neighbors like `LIVEKIT_API_SECRET` and `OPENCLAW_TOKEN`.
- Added a parametric pytest (`test_production_schema_marks_provider_api_keys_secret`) that loads the **production** schema (not a fixture) and asserts the flag on each of the five keys. Uses `pathlib.Path(__file__).resolve().parents[4]` for cross-platform path resolution.

## Testing
- [x] `jq . dream-server/.env.schema.json` — parses cleanly
- [x] `python3 -m pytest extensions/services/dashboard-api/tests/test_settings_env.py -v` — **16/16 pass** (11 pre-existing + 5 new parametric)
- [x] `make lint` — clean
- [x] P  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
