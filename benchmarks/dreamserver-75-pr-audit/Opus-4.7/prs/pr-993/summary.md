# PR #993 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-cli): color-escape + table-separator + NO_COLOR spec

## Author's stated motivation

The PR body says (paraphrased):

> ## What

Three visual-polish fixes for `dream-cli`:

1. ANSI-C quoting (`$'\033[...'`) for color variables + `TTY && NO_COLOR`-guarded color emission, so color codes don't leak as literal escape text into non-ANSI-processing contexts (notably `cmd_help`'s heredoc, and piped/redirected output).
2. Table separators rendered at correct column widths via a new `hr <width>` helper using `printf -v` + parameter expansion.
3. `NO_COLOR` check uses `${NO_COLOR+x}` per [no-color.org spec](https://no-color.org/) (empty-string variable counts as "set"); `cmd_preset list` adopts the same separator helper for consistency.

## Why

`dream help` was printing literal `\033[0;34mDream Server CLI...` to terminals because single-quoted color vars held the escape string, not the ESC byte, and heredocs don't process `\033`. Short separator dashes made `dream list`, `dream template list`, and `dream preset list` headers appear broken on wider terminals.

## How

Three commits, each self-contained with full rationale:

- `d52cb120` — `$'\033[0;31m'`-style ANSI-C quoting + TTY+NO_COLOR guard block.
- `7c407c0a` — `hr()` helper using `printf -v` + `${var// /<char>}` parameter expansion; dynamic-width `_template_list`.
- `9cba4879` — spec-strict NO_COLOR check (`${NO_COLOR+x}`) + `cmd_preset list` separator.

## Testing

- `dream help`, `dream list`, `dream template list`, `dream preset list` render cleanly on macOS Terminal.app and iTerm2.
- `dream help > file.txt` emits zero escape codes (TTY-guard   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
