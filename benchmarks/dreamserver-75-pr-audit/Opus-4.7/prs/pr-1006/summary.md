# PR #1006 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-cli): route log() and warn() to stderr so command captures remain clean

## Author's stated motivation

The PR body says (paraphrased):

> ## What
`dream-cli`'s `log()` and `warn()` helpers wrote to stdout. `dream
benchmark` captures `cmd_chat`'s stdout to measure LLM response time,
so the `[dream] Sending to <model>...` info line emitted inside
`cmd_chat` leaked into the captured response string. Output looked
like:

```
Response: [dream] Sending to local...
Hello World
```

## Why / How
Appended `>&2` to the two helpers. This follows Unix convention
(informational messages on stderr) and cleanly separates status
text from data. The only `\$(cmd_*)` capture in the entire 3418-line
file (`cmd_benchmark` line 1174) already uses `2>/dev/null`, so the
log banner is now cleanly discarded before display — response
contains only the LLM reply.

JSON-emitting paths (`cmd_status_json`, `cmd_doctor --json`,
`cmd_audit --json`) do not invoke `log` / `warn` before emitting
JSON, so machine-readable output is unchanged.

Scope intentionally minimal. Only `log()` and `warn()` changed;
`success()`, `error()`, and `log_warn()` remain on stdout.

## Testing
- `bash -n` passes.
- No new shellcheck warnings at the touched lines.
- Repo-wide scan confirms no script / test captures `dream-cli`
  stdout expecting `[dream]` or `⚠` prefixes — zero consumers to
  break.

## Manual test
`dream benchmark local` → the `Response:` line no longer contains
`[dream] Sending to <model>...`.

## Platform Impact
- macOS / Linux / Windows WSL2: `>&2` is POSIX; identical behavior
  on all three platforms.

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
