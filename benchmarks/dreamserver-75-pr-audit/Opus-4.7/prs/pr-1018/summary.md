# PR #1018 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> test(dream-cli): BATS regression shield for 5 dream-cli / supporting behaviors

## Author's stated motivation

The PR body says (paraphrased):

> ## ⚠️ Draft — depends on 5 upstream PRs merging first

Each test file pins behavior introduced by a different unmerged PR. Merge order below:

| Test file | Pins behavior from |
|---|---|
| `test-config-masking.bats` | #994 — `_cmd_config_is_secret` + schema cache |
| `test-compose-summary-wrapper.bats` | #1016 — `_compose_run_with_summary` (was #1001 — closed/superseded) |
| `test-dream-cli-flags.bats` | #998 + #1002 — `set -euo pipefail` + nounset guards |
| `test-functional-resilience.bats` | #1003 — `dream-test-functional.sh` set-e resilience |
| `test-sr-resolve.bats` | #1016 — `sr_resolve` prefix-strip (was #1001 — closed/superseded) |

Once all 5 merge (#994, #998, #1002, #1003, #1016), rebase drops the merge commits and the PR diff becomes exactly 5 new `.bats` files (+890 LoC total, zero existing-file edits).

**Note (apr-25):** the original #1001 was closed in favor of its superset #1016; the test files in this PR target the same `_compose_run_with_summary` and `sr_resolve` behavior, which now ships in #1016. No code change needed in this PR — only the rebase target shifts to post-#1016 main.

## What
5 new BATS test files in `dream-server/tests/bats-tests/` locking in the post-PR-12 dream-cli refactors:

- **test-config-masking.bats** (17 cases) — `_cmd_config_is_secret` behavior from both `dream config show` and `dream preset diff` paths. Covers schema-driven masking, 7-keyword fallback (`secret/password/pass/token/key/salt/bearer`), case-insensitive, missing+malf  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
