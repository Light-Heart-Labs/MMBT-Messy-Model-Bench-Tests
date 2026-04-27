# PR #1033 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(extensions): align librechat MONGO_URI guard; remove :? from jupyter command

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Two one-line fixes to community extension `:?` interpolation guards.

## Why
- **librechat** asymmetry: the `librechat-mongodb` service uses `${LIBRECHAT_MONGO_PASSWORD:?}` at initdb, enforcing a real password. But the `librechat` service's `MONGO_URI` interpolated the same variable without `:?` — so when unset, `librechat` connected with `librechat:@` (empty password) while the DB required a real one. Operators hit silent MongoDB auth errors with no clear diagnostic.
- **jupyter** pull-poisoning: `${JUPYTER_TOKEN:?}` was in both `environment:` and `command:`. Docker Compose evaluates `:?` at stack-level parse time, so an unset `JUPYTER_TOKEN` aborted any `docker compose config/up/pull/...` operation on a merged stack that happened to include jupyter — even when the operator was working on a completely unrelated service. Runtime-verified with `docker compose config` that the `command:` block alone triggers the error.

## How
1. `librechat/compose.yaml:11` — change the MONGO_URI password reference to `${LIBRECHAT_MONGO_PASSWORD:?LIBRECHAT_MONGO_PASSWORD must be set}`, matching the convention already used everywhere else in the same file.
2. `jupyter/compose.yaml:14` — strip the `:?` from the `command:` block, keeping the `environment:` block's `${JUPYTER_TOKEN:?...}` as the single guard. Presence is still enforced at parse time; the poisoning path via `command:` is gone.

## Testing
- Runtime: `unset JUPYTER_TOKEN && docker compose -f jupyter/compose.yaml config` befor  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
