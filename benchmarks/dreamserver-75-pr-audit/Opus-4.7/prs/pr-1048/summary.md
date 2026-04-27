# PR #1048 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(macos): replace backticks with single quotes in env-generator comment

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Replace backticks with single quotes at `installers/macos/lib/env-generator.sh:262` so the comment is no longer evaluated as a command substitution by the heredoc.

## Why
The .env-generation heredoc terminator at line 181 is `<< ENVEOF` — **unquoted**. That means Bash performs both variable expansion AND command substitution on the heredoc body. Variable expansion is intentional (lines 182–276 contain dozens of legitimate `${TIER_NAME}`, `$(if ... then ... fi)`, `${webui_secret}` references — quoting the terminator would break the entire heredoc).

The accidental side-effect: any literal backticks in the heredoc body are also evaluated. Line 262 contained:
```
# post-install: `dream enable langfuse`.
```
Which Bash interpreted as `` `dream enable langfuse` ``. The `dream` CLI is not yet on PATH at install time, so the install log emitted `dream: command not found` AND the empty result of the failed substitution was written into `.env`, silently truncating the comment to `# post-install: .` (the words `dream enable langfuse` disappear entirely).

## How
Single-character-class change at line 262:
```
- # post-install: `dream enable langfuse`.
+ # post-install: 'dream enable langfuse'.
```

Single quotes match the in-file convention at line 245 (`# here and run 'dream-macos.sh restart' to use a different model.`).

**Verified clean elsewhere:**
- `installers/phases/06-directories.sh:216` has the identical comment text but is OUTSIDE any heredoc → backticks inert there.   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
