# PR #1000 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> feat(dream-cli): --json flag on list/status and document doctor --json

## Author's stated motivation

The PR body says (paraphrased):

> ## What

`dream list --json` and `dream status --json` now work as advertised. Previously the `--json` flag was silently dropped because the main case dispatch forwarded no arguments to the subcommands. Also documents the previously-undocumented `dream doctor --json`, keeps `dream status-json` as a back-compat hyphenated alias.

## Why

Scripts piping `dream list` / `dream status` output to `jq` got parse errors because the subcommands emitted human-readable output regardless of any flag passed. The human-readable hyphenated alias `dream status-json` was the only JSON-emitting path; `--json` appeared to work (no error) but emitted the wrong format.

## How

Single commit `46df7641`:

- Main case dispatch now forwards `"$@"` to both `cmd_list` and `cmd_status`.
- `cmd_list --json` emits a JSON array of `{id, category, status}`.
- `cmd_status --json` delegates to the existing `cmd_status_json`. The delegation is wrapped in a subshell (`( cmd_status_json )`) to isolate the RETURN trap set inside `cmd_status_json` — without the subshell, the trap would leak into `cmd_status`'s frame and crash with an unbound-variable error when the sibling nounset PR lands on top.
- Unknown flags on these subcommands now error cleanly (exit 1).
- `cmd_help` advertises the new flags and the existing `doctor --json`.

## Testing

- `dream list --json | jq '.'` and `dream status --json | jq '.'` both parse successfully.
- Isolated sandbox repro under `set -euo pipefail` confirms subshell isolation p  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
