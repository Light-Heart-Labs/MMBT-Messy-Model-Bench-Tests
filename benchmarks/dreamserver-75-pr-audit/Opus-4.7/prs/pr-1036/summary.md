# PR #1036 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> chore(extensions-library): remove community privacy-shield (dead code)

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary
- Deletes the community-variant `resources/dev/extensions-library/services/privacy-shield/` (8 files, 598 LOC).
- Removes 2 table rows from `resources/dev/extensions-library/README.md` (catalog + compatibility matrix) and updates the "33 service extensions" prose counts to 32.
- The authoritative built-in at `dream-server/extensions/services/privacy-shield/` is untouched.

## Why a delete
The community variant cannot be installed via the dashboard: `_scan_compose_content` in `routers/extensions.py` rejects any compose declaring a service whose name is in `CORE_SERVICE_IDS` (which includes `privacy-shield`, per `config/core-service-ids.json`). So the file existed as reference code but contained multiple regressions vs the built-in:

- `/health` + `/stats` exposed `target_api`, `active_sessions`, `total_pii_scrubbed` **without authentication** (built-in gates these behind `_is_authenticated`).
- Ephemeral `SHIELD_API_KEY` regenerated every container restart (no persistence via `SHIELD_API_KEY_PATH`).
- Bare `127.0.0.1:` port binding violates PR #964's `${BIND_ADDRESS:-127.0.0.1}:` pattern.
- Missing `compatibility.dream_min`.

Removing the reference is safer than letting users find it and attempt a manual install that would ship those regressions.

## Platform Impact
- **macOS / Linux / Windows-WSL2**: identical. Filesystem-only delete in `resources/dev/`; no code, compose, installer, or CI behavior changes.

## Testing
- `make lint` → All lint checks passed.
- `pre-  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
