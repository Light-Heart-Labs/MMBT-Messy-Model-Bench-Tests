# PR #1008 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> refactor(dream-cli): guard .env grep pipelines against pipefail kill on missing keys

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Seven `grep "^KEY=" .env | cut | tr` pipelines in `dream-cli` would
exit 1 when the key is absent. Under `set -eo pipefail` those
pipelines would kill the script before the downstream defensive
checks (`[[ -n ... ]]`, `${var:-(not set)}`) can handle the
empty-on-miss case the surrounding code was written for.

## Why
The surrounding code treats missing keys as benign (empty string,
"not set" default, fallthrough to defaults). That contract held
pre-pipefail because a grep miss yielded an empty pipeline output
with exit 0. Post-pipefail, a grep miss propagates exit 1, and
because these pipelines are assigned with bare `VAR=$(...)` (not
`local VAR=$(...)`, which would mask the exit status), `set -e`
kills the script mid-flow.

## How
Appended `|| true` to each of the seven pipelines:

| line | function                | key read             |
| ---- | ----------------------- | -------------------- |
| 254  | `_check_version_compat` | `DREAM_VERSION`      |
| 836  | `cmd_dry_run`           | `DREAM_VERSION`      |
| 849  | `cmd_dry_run`           | `DASHBOARD_API_KEY`  |
| 938  | `cmd_dry_run` loop      | model-related keys   |
| 953  | `cmd_dry_run` loop (2)  | model-related keys   |
| 1434 | `cmd_enable`            | `GPU_BACKEND`        |
| 1781 | `cmd_preset`            | `DREAM_MODE`         |

Line 254 additionally swaps `| head -1` for `| sed -n '1p'` —
SIGPIPE-safe under pipefail, portable across BSD and GNU sed.

Line 1434 additionally picks up a missing `2>/dev/  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
