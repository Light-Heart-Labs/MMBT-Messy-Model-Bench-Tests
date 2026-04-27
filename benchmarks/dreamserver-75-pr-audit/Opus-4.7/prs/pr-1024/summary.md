# PR #1024 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> refactor(scripts): array-expand COMPOSE_FLAGS for SC2086 + glob safety

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Convert `$COMPOSE_FLAGS` (and `$ENV_FILE_FLAG`) from unquoted string expansion to bash array expansion in three operational scripts: `validate.sh`, `dream-preflight.sh`, and `validate-compose-stack.sh`.

## Why
All three scripts passed `$COMPOSE_FLAGS` unquoted to `docker compose`, producing SC2086 shellcheck warnings and leaving flag values subject to glob expansion (filename generation) before reaching the command. No structural mechanism prevented a flag value containing wildcard characters from being mangled silently.

## How
In each script, immediately after `COMPOSE_FLAGS` is populated from `resolve-compose-stack.sh`, add:
```bash
read -ra COMPOSE_FLAGS_ARR <<< "$COMPOSE_FLAGS"
```
Then replace every `docker compose $COMPOSE_FLAGS …` site with `docker compose "${COMPOSE_FLAGS_ARR[@]}" …`.

In `validate-compose-stack.sh`, `ENV_FILE_FLAG` (previously a bare string) is also converted to an array: `ENV_FILE_FLAG_ARR=(--env-file "$ENV_FILE")`.

In `validate.sh`, two call sites (L64/65) previously routed through `check()`, which executes its argument via `bash -c "$cmd"` — array boundaries are lost across that string handoff. Those two checks are inlined as direct `if/grep` pipelines so array expansion applies correctly. The `check()` function and all its other callers are untouched.

## Testing
- Automated: `bash -n` clean on all three files; 4 SC2086 shellcheck warnings eliminated; all 45 preflight tests pass.
- Manual: Run `dream-server/scripts/validate.sh` and `dr  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
