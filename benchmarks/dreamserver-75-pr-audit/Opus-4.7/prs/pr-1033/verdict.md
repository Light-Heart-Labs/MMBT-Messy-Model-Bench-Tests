# PR #1033 — Verdict

> **Title:** fix(extensions): align librechat MONGO_URI guard; remove :? from jupyter command
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/librechat-jupyter-env-guards`
> **Diff:** +2 / -2 across 2 file(s) · **Risk tier: Trivial (score 1/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1033

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **1** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Two surgical fixes to compose `:?` interpolation guards. (1) `librechat/compose.yaml:11` adds the missing `:?` on the `MONGO_URI` password reference so the previously-silent "empty password vs. db-required-password" auth mismatch becomes a parse-time error. (2) `jupyter/compose.yaml:14` removes a duplicate `:?` from the `command:` line — Compose evaluates `:?` at stack-parse time, so an unset `JUPYTER_TOKEN` was poisoning unrelated `compose config/up/pull` operations on any merged stack including jupyter. The single guard in `environment:` still enforces presence.

## Findings

- **Empty-token risk neutralized:** the env-block `:?` blocks unset/empty at parse time, so `--NotebookApp.token=` (empty) can never run. Verified by the PR body's reasoning about the parse-time gate.
- **Sweep already done:** PR body claims zero other `${VAR:?}` in `command:` or `entrypoint:` blocks repo-wide. Spot-check on the diff confirms this is a targeted single-instance fix.
- **`LIBRECHAT_MONGO_PASSWORD` auto-generated** by `librechat/setup.sh` via `openssl rand`, so fresh installs are unaffected; the fix protects against operators who edit `.env` and remove the line.

## Cross-PR interaction

- No file overlap with other open PRs in this batch. Both files are in `resources/dev/extensions-library/services/`.
- Part of the disjoint extension-fixes group (#1027/#1028/#1029/#1032/**#1033**/#1034) — could collapse with #1032 + #1034 into a single sweep PR per dependency-graph suggestion.

## Trace

- `services/librechat/compose.yaml:11` — `${LIBRECHAT_MONGO_PASSWORD}` → `${LIBRECHAT_MONGO_PASSWORD:?...}`
- `services/jupyter/compose.yaml:14` — drop `:?` from `command:` (single guard preserved in `environment:` at line 12)
