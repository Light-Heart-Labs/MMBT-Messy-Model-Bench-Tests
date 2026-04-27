# PR #990 — Verdict

> **Title:** chore(deps): bump actions/github-script from 8.0.0 to 9.0.0
> **Author:** [app/dependabot](https://github.com/app/dependabot) · **Draft:** False · **Base:** `main`  ←  **Head:** `dependabot/github_actions/actions/github-script-9.0.0`
> **Diff:** +5 / -5 across 2 file(s) · **Risk tier: Trivial (score 0/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/990

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

**HOLD — needs maintainer judgment.** This is a SHA-pinned `actions/github-script@v8 → @v9` major-version bump in two CI workflows. v9 is a documented breaking change: `@actions/github` is now ESM-only, so `require('@actions/github')` no longer works inside scripts, and `getOctokit` is now an injected parameter. The five `script: |` blocks in `autonomous-code-scanner.yml:1222-1257` and `claude-review.yml:219-460` need to be inspected to confirm they don't use `require('@actions/github')` or shadow `const getOctokit = ...`. Maintainer should grep before merging.

## Findings

- **Breaking change risk is concrete and called out by the upstream release notes.** The dependabot body excerpts the v9 release notes verbatim: `require('@actions/github')` will fail at runtime, and `const/let getOctokit = ...` declarations will throw `SyntaxError`. The five script blocks in this repo's workflows post issue/PR comments using `github.rest.issues.createComment(...)` style — that's the standard pattern that v9 supports unchanged. But verification still requires reading each `script: |` block.
- **SHA-pinning is correct.** Both touched lines pin `@3a2844b7e9c422d3c10d287c895573f7108da1b3` (the v9.0.0 commit). Best-practice GitHub Actions hygiene; matches the repo's pattern of SHA-pinning third-party actions.
- **No CI signal yet.** Dependabot PRs typically run only `lint-shell.yml` etc.; the workflows touched are not exercised on PR (they run on schedule / on `failure()`). So CI green here doesn't catch the runtime breakage. The first time we'd see it is the next time `autonomous-code-scanner.yml` actually fails and tries to create an issue.

## Cross-PR interaction

- No file overlap with any non-dependabot PR in this batch. Pure CI infrastructure update.
- Same family as PR #991 (Anthropic claude-code-action bump) — independent dependencies.

## Trace

- `.github/workflows/autonomous-code-scanner.yml:1225, 1260` — both `actions/github-script` invocations bumped to v9 SHA.
- `.github/workflows/claude-review.yml:222, 424, 463` — three `actions/github-script` invocations bumped to v9 SHA.
- The v9 release notes (in PR body): `require('@actions/github')` no longer works; `getOctokit` is now injected. **Maintainer: grep the five `script: |` blocks for `require('@actions/github')` and for `const getOctokit` / `let getOctokit` before merging.**
