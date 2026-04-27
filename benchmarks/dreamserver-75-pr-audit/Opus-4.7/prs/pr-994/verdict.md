# PR #994 — Verdict

> **Title:** fix(dream-cli): schema-driven secret masking + macOS Bash 4 validation
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dream-cli-config-security-macos`
> **Diff:** +89 / -15 across 4 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/994

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Four correct, well-scoped fixes. (1) `dream-cli:1090-1105` — new `_cmd_config_load_secret_schema` reads `.env.schema.json` via jq and populates an array of keys with `"secret": true`. (2) `dream-cli:1107-1119` — new `_cmd_config_is_secret` checks the schema array first, falls through to the keyword pattern `*secret*|*password*|*pass*|*token*|*key*|*salt*|*bearer*` if the schema didn't classify the key. (3) `dream-cli:1156-1163` — `dream config validate` now invokes `validate-env.sh` through `"$BASH"` (the running interpreter, guaranteed Bash 4+ by the line-21 version check), and `validate-env.sh:7-22` adds its own Bash-4 guard for direct invocations. macOS-only crash on `declare -A` fixed. (4) `dream-cli:2079` — `cmd_preset diff` now uses the same `_cmd_config_is_secret` helper instead of a narrower regex; previously this code path leaked `LANGFUSE_SALT`, `LANGFUSE_DB_PASSWORD`, etc. to terminal in plaintext on `dream preset diff`. `.env.schema.json` marks `N8N_USER` and `LANGFUSE_INIT_USER_EMAIL` as `secret: true` (admin email = identity material; correct call).

## Findings

- **The `2>/dev/null` on the jq calls are defensive, not silent-catch regressions.** `_cmd_config_load_secret_schema` uses `2>/dev/null` on the jq parse so a malformed schema doesn't blow up `dream config show` — and the PR is explicit about the fallback behavior: if jq returns nothing, `_cmd_config_schema_loaded` stays 0, and the keyword pattern runs. The fallback path is the schema-miss path, not a silent-catch. CLAUDE.md's "no broad catches" rule is satisfied because the failure surface is bounded (any unrecognized key is *over-masked* via the keyword regex, never *under-masked*).
- **The `secret: true` flip on `N8N_USER` / `LANGFUSE_INIT_USER_EMAIL` is borderline-aggressive but defensible.** `N8N_USER` is the n8n admin email; `LANGFUSE_INIT_USER_EMAIL` is the Langfuse admin email. Treating them as secrets in `dream config show` matches the project's "default to over-masking" stance. PII protection beats one-line clarity. PR #1010 (provider API keys → secret) is the analogous metadata-flip pattern.
- **Convention adherence:** No `eval`, no new `2>/dev/null` outside the schema-load path described above, no retry chains, no port bindings. Schema rule is honored — modifies both `.env.schema.json` and `dream-cli` (the consumer).

## Cross-PR interaction

- Touches `dream-cli` — same Cluster 1 conflict surface as #993, #997, #998, #999, #1000, #1002. Per dependency graph, this PR sits at "step 5" in the strict-mode chain. Textual conflicts only; merge order is mechanical.
- Touches `.env.schema.json` — Cluster 5 disjoint adds. `N8N_USER` and `LANGFUSE_INIT_USER_EMAIL` get a new field (`secret: true`), but no new keys. Compatible with #988, #1010, #1013, etc.
- Touches `tests/test-validate-env.sh` — no other open PR modifies this; clean.

## Trace

- `dream-server/dream-cli:1090-1119` — `_cmd_config_load_secret_schema` + `_cmd_config_is_secret` helpers (file-scope, used by both `cmd_config show` and `cmd_preset diff`).
- `dream-server/dream-cli:1158-1162` — `validate-env.sh` invoked through `"$BASH"`.
- `dream-server/dream-cli:2079` — `cmd_preset diff` mask logic now calls `_cmd_config_is_secret` (was: narrower `(PASSWORD|SECRET|KEY|TOKEN|API)` regex that missed `_PASS`, `_SALT`).
- `dream-server/scripts/validate-env.sh:11-22` — Bash-4+ runtime guard with macOS-specific install-bash hint.
- `dream-server/.env.schema.json:78, 501` — `secret: true` on `N8N_USER` and `LANGFUSE_INIT_USER_EMAIL`.
