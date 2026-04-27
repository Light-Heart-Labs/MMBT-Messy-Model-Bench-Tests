# PR #1048 — Verdict

> **Title:** fix(macos): replace backticks with single quotes in env-generator comment
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/macos-env-generator-backtick`
> **Diff:** +1 / -1 across 1 file(s) · **Risk tier: Trivial (score 0/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1048

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **0** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE**

One-character class swap on a real defect. The heredoc terminator at L181 is unquoted (`<< ENVEOF`), so command substitution applies to the whole body — and the backticks in `` ` ``dream enable langfuse`` ` `` were being executed at install time, emitting `dream: command not found` to the install log and silently truncating the comment in the generated `.env` to `# post-install: .`. Single quotes match the in-file convention at L245. The PR body verifies that the duplicate comment in `installers/phases/06-directories.sh:216` is outside any heredoc (so backticks are inert there).

## Findings

- Diff is one line (diff.patch:9-10). No functional risk; comment-only.
- Heredoc terminator deliberately remains unquoted because L182-276 use legitimate `${VAR}` expansion. Quoting it would have been a much larger change.

## Cross-PR interaction

- No file overlaps with other open PRs.

## Trace

- `installers/macos/lib/env-generator.sh:262` — backtick → single-quote swap inside `<< ENVEOF` heredoc
