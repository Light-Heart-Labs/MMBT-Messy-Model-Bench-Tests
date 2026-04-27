# PR #1010 — Verdict

> **Title:** chore(schema): mark provider API keys as secret in .env.schema.json
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `chore/schema-secret-flip`
> **Diff:** +39 / -5 across 2 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1010

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Adds `"secret": true` to five provider API-key entries in
`.env.schema.json` (`TARGET_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`TOGETHER_API_KEY`, `LIVEKIT_API_KEY`) at lines 56-78 and 414, and adds a
parametric pytest at `test_settings_env.py:312-339` that loads the production
schema and asserts the flag for each. Today these keys are already masked via
`dream config show`'s inline grep on `key=` and dashboard-api's
`_is_secret_field` regex fallback — both pattern-match `API_KEY` in the name.
The schema flag routes the masking through the authoritative path so a future
rename that breaks the name pattern doesn't silently stop masking.

## Findings

- No runtime behavior change. Both pattern-matching paths and the
  schema-driven path produce the same masked output today; this just routes
  through the primary one.
- The new test loads the *production* schema (not a fixture) and uses
  `pathlib.Path(__file__).resolve().parents[4]` for cross-platform resolution.
  Robust against CI working-directory drift.
- Schema-only metadata flip; `.env.example` is intentionally not modified
  (these keys are already documented; `secret` is a schema property, not a
  user-facing default). Does not run afoul of the
  "schema changes must update both" convention because no key is being added
  or renamed.
- `LIVEKIT_API_KEY` getting the flag closes a gap with `LIVEKIT_API_SECRET`,
  which already had it. Consistency win.

## Cross-PR interaction

- `.env.schema.json` is also touched by #750, #988, #994, #1017, #1018. None
  of those mark the same five keys; conflicts are textual (insertion order in
  JSON) and mechanical. Per dependency-graph, no semantic conflict.
- If #994 or #988 introduce additional secret-bearing keys, they should
  follow this PR's pattern. Land #1010 first as the precedent.

## Trace

- `dream-server/.env.schema.json:56,61,66,71,414` — five entries flipped
- `dream-server/extensions/services/dashboard-api/tests/test_settings_env.py:312-339`
  — new parametric regression guard
