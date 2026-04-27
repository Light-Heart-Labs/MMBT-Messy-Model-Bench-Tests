# PR #994 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-cli): schema-driven secret masking + macOS Bash 4 validation

## Author's stated motivation

The PR body says (paraphrased):

> ## What

Four related hardenings to `dream config` and its helpers:

1. **Schema-driven masking in `dream config show`** — replace the narrow keyword regex (which missed `_PASSWORD`, `_SALT`, `_PASS` suffixed fields) with `.env.schema.json`-driven detection.
2. **Bash 4+ invocation** — `dream config validate` now invokes `validate-env.sh` through `"$BASH"`, and the target script adds its own Bash-4 guard. Fixes a macOS-only crash under `/bin/bash` 3.2.
3. **Belt-and-suspenders fallback** — after a schema-miss under `_schema_loaded=1`, fall through to the keyword match instead of returning "not secret." Covers schema gaps and malformed schemas.
4. **Helper promoted to file-scope + reused by `dream preset diff`** — `_cmd_config_is_secret` was nested inside `cmd_config show`, so `dream preset diff` still used the original narrow regex and leaked `N8N_PASS`, `LANGFUSE_SALT`, and admin email fields in plaintext. Helper is now file-scope; both commands use it. `N8N_USER` and `LANGFUSE_INIT_USER_EMAIL` are also marked `secret: true` in `.env.schema.json`.

## Why

The narrow regex `(SECRET|PASS|KEY|TOKEN)=` missed suffix-form names like `LANGFUSE_DB_PASSWORD`, `LANGFUSE_SALT`, `OPENCODE_SERVER_PASSWORD`, etc. `dream config validate` crashed on every fresh macOS install because `validate-env.sh` uses `declare -A` (Bash 4+ only) but was invoked through `/bin/bash` 3.2. And `dream preset diff` was a forgotten sibling code path.

## How

Four commits, each self-contained:

- `a9e87239`   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
