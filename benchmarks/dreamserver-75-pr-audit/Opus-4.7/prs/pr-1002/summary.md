# PR #1002 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> refactor(dream-cli): enable set -u and add guards for conditional variables

## Author's stated motivation

The PR body says (paraphrased):

> ## What

Enable `set -u` (nounset) in `dream-cli` on top of the existing `set -eo pipefail` foundation. Audit every variable read; add `${VAR:-}` guards to six legitimately-conditional sites (missing positional args for `preset diff`, sparse associative-array lookups when comparing preset ext/env maps, registry lookups for service dirs without valid manifests). All other variables in the file are unconditionally set before use; no guard added elsewhere.

## Why

Nounset catches typos in variable names at runtime instead of silently expanding to empty strings. The audit also surfaced three pre-existing latent bugs that `set -u` would have caught immediately:

- `preset diff`: bare `$2` / `$3` crashed with no args.
- `preset diff`: `ext1[$key]` / `env1[$key]` associative-array reads crashed partway through comparison when a key exists only in the other preset.
- `enable <svc>`: bare `SERVICE_DEPENDS[$service_id]` crashed for service directories that exist on disk but have no valid manifest (edge case: user-extensions with malformed manifest).

## How

Single commit (tip `bea96fe2`; the original `a7bd6cac` was rebased onto this PR's parent branch `fix/dream-cli-pipefail-exit-codes` after that branch's commits were adjusted during review — PR-11's nounset audit content is unchanged, only the base commits it sits on have updated SHAs).

Audited by running every read-only subcommand end-to-end in a fake `INSTALL_DIR` and against a live install: `help`, `version`, `list`, `status`,   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
