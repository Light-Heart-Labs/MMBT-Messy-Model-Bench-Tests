# PR #998 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-cli): pipefail + surface LLM failures + exit-code contract

## Author's stated motivation

The PR body says (paraphrased):

> ## What

Three independent error-discipline improvements to `dream-cli`:

1. Promote shell options from `set -e` to `set -eo pipefail`, aligning with CLAUDE.md's project standard. Audit `| head -1` sites (converted to `| sed -n 1p` for SIGPIPE-safety).
2. `dream chat` and `dream benchmark` now actually detect LLM failures instead of silently reporting "success" against a dead backend. Uses `curl --fail --show-error --max-time` + `jq -er` strict parsing, plus a `/v1/models` preflight probe.
3. Three commands (`dream disable`, `dream agent logs`, `dream gpu reassign`) now exit non-zero on failure/skip conditions, fixing the exit-code contract for scripted callers.

## Why

Before this PR: `dream chat` against a dead backend printed `[dream] Sending to ...`, emitted an empty line, and exited 0. `dream benchmark` propagated that silent failure and happily reported sub-second "Excellent" performance against a non-running LLM. Root cause: curl was invoked with `-s` (silent, no error-show, no fail-on-HTTP-error) and responses were parsed with `jq -r .choices[0].message.content // .error.message // "Error: no response"` — every failure path masked behind a human-friendly string on stdout.

`dream disable bogus-service` used to silently stop a non-existent container (`|| true`) and print a success-shaped message. Several other commands exited 0 after warning about skip conditions, so automation couldn't distinguish "success" from "skipped."

## How

Three commits, each self-contained:  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
