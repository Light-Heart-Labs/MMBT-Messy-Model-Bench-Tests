# PR #1011 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> chore(bash32): guard declare -A callers + route dream-cli validate through $BASH

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Adds Bash 4+ guards to five scripts that use `declare -A` without one, and routes two `dream config validate` subprocesses through `"$BASH"` so they inherit dream-cli's modern bash interpreter.

Files touched (6):
- `dream-server/scripts/pre-download.sh` — Pattern A guard (bare `exit 1`)
- `dream-server/scripts/dream-test-functional.sh` — Pattern A guard + drop dead `2>/dev/null || true` fallback on `declare -A SERVICE_PORTS`
- `dream-server/scripts/validate-env.sh` — Pattern A guard
- `dream-server/lib/progress.sh` — Pattern B guard (`return 1 2>/dev/null || exit 1`)
- `dream-server/installers/phases/03-features.sh` — Pattern B guard
- `dream-server/dream-cli` — prefix validate-env.sh and validate-manifests.sh subprocess execs with `"$BASH"`

Guard style mirrors `dream-cli:8-14` (Pattern A, standalone scripts) and `lib/service-registry.sh:18-24` (Pattern B, sourced libraries).

## Why
On macOS, system `/bin/bash` is 3.2.57, which does not support associative arrays. Two user-facing problems:

1. Invoking any of these scripts directly under system bash (e.g. `./scripts/pre-download.sh --tier 3` from FAQ.md) produced a cryptic `declare -A: invalid option` crash with no actionable hint.
2. Even when dream-cli itself was launched under a modern Homebrew bash (its own Bash 4+ guard passes), it invoked `scripts/validate-env.sh` via shebang — which re-resolves to `/bin/bash` 3.2 regardless of the parent interpreter. `dream config validate` was silently non-functional on mac  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
