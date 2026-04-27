# PR #1049 — Verdict

> **Title:** fix(jupyter): convert command to exec-form list to avoid shell splitting
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/jupyter-exec-form-command`
> **Diff:** +9 / -1 across 1 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1049

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE**

Defensive hardening, correctly executed. Of the 4 community extensions with `command:`, jupyter was the only one still using shell-form — Compose hands shell-form to `/bin/sh -c`, which word-splits whitespace in `$JUPYTER_TOKEN`. The default token is auto-generated 64-char hex (no metacharacters), so this is a latent bug, not an active one. The exec-form list at diff.patch:10-18 brings jupyter into line with aider/open-interpreter/milvus. Crucial detail: `--NotebookApp.password=''` (shell-form) became `--NotebookApp.password=` (diff.patch:15) — writing `''` as a list element would pass two literal single-quote chars, not "no password." The author caught this.

## Findings

- File is in `resources/dev/extensions-library/` (community library, not the deployed `dream-server/`). Smaller blast radius — only affects users who install jupyter via dashboard.
- PR body acknowledges the bare `127.0.0.1:` port mapping pre-dates this PR; correctly out of scope (filed as fork issue #504).

## Cross-PR interaction

- No file overlaps with other open PRs.

## Trace

- `resources/dev/extensions-library/services/jupyter/compose.yaml:14-22` — shell-form scalar → exec-form YAML list, with empty-password literal preserved at L18
