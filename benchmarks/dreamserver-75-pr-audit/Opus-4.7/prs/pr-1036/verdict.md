# PR #1036 — Verdict

> **Title:** chore(extensions-library): remove community privacy-shield (dead code)
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `chore/remove-community-privacy-shield`
> **Diff:** +2 / -602 across 9 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1036

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **4** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Deletes 598 LOC of community-variant `privacy-shield` that was structurally uninstallable: `_scan_compose_content` in `routers/extensions.py` rejects any compose declaring a service whose name is in `CORE_SERVICE_IDS` (which includes `privacy-shield`). The community variant therefore could never reach a user's stack via the dashboard installer — but its existence in the library directory exposed three regressions a manual installer could ship: `/health` and `/stats` returning `target_api`/`active_sessions`/`total_pii_scrubbed` without authentication (built-in gates these), ephemeral `SHIELD_API_KEY` regenerated every container restart, and a hardcoded `127.0.0.1:` port binding violating the BIND_ADDRESS pattern. README counts updated 33→32 in two places.

## Findings

- **Defense-in-depth retained:** `EXCLUDED_IDS = {"privacy-shield"}` at `resources/dev/scripts/generate-extensions-catalog.py:21` is left in place — accidental directory reintroduction won't silently re-add to the catalog.
- **The authoritative built-in at `dream-server/extensions/services/privacy-shield/` is untouched.** Confirmed in PR body and verified by file paths in diff (only `resources/dev/extensions-library/` paths affected).
- **Deletion is the right call** vs. trying to fix the community variant. The variant exposed unauthenticated `/stats` returning `total_pii_scrubbed` — a privacy regression on a privacy product. Not worth keeping as reference.

## Cross-PR interaction

- **Soft conflict with #1027** on `resources/dev/extensions-library/services/privacy-shield/compose.yaml`. #1027 modifies that file's port-binding line; this PR deletes the file entirely. If #1027 lands first, #1036 still applies cleanly (delete subsumes the port edit). If #1036 lands first, #1027 needs to drop privacy-shield from its sweep (29→28 services touched). Maintainer should coordinate or land #1036 first.
- No conflict with other PRs in this batch.

## Trace

- `resources/dev/extensions-library/services/privacy-shield/` — 8 files deleted (Dockerfile, PII_COVERAGE.md, README.md, compose.yaml, manifest.yaml, pii_scrubber.py, proxy.py, requirements.txt)
- `resources/dev/extensions-library/README.md:3, 83, 117, 204` — count updates 33→32 + two table rows removed
- `resources/dev/scripts/generate-extensions-catalog.py:21` (existing, retained) — `EXCLUDED_IDS` defense-in-depth
