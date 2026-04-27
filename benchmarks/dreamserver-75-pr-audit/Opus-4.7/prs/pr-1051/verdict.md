# PR #1051 — Verdict

> **Title:** fix(resolver): hoist yaml import, guard empty manifests, align user-ext loop
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `fix/resolver-python-hygiene`
> **Diff:** +76 / -10 across 1 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1051

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — needs maintainer judgment**

The three changes are individually correct and small. (1) The yaml hoist (diff.patch:8-14) deduplicates the import and pre-positions for #1029. (2) The `isinstance(manifest, dict)` guard (diff.patch:32-34, 62-64) prevents `AttributeError` on empty/comment-only manifests — `yaml.safe_load` returns `None` for those and the existing narrow exception handler doesn't catch `AttributeError`. (3) The user-ext loop alignment (diff.patch:67-96) brings .disabled, compose.local.yaml, and compose.multigpu.yaml handling into parity. **The hold is structural**: the PR body explicitly requires merge after #1029, and the user-ext loop deliberately omits `gpu_backends` filtering to avoid mechanical conflict — so this can't merge before #1029 anyway. Also, the new loop uses a broad `except Exception` (diff.patch:98) that re-raises only after narrow detection — defensible per the project's "narrow exceptions at I/O boundaries" rule, but worth maintainer eyes.

## Findings

- The compat carve-out at diff.patch:67-69 (manifest-less user extensions get `service = {}` defaults) is a deliberate, documented asymmetry with the built-in loop. PR body calls this out clearly.
- Empty manifest in **built-in** loop (diff.patch:34) skips silently with a warning; in user-ext loop, only non-None non-dict triggers the warning. Documented decision; preserves backward compat for legacy user extensions.
- `except Exception as e` at diff.patch:98 with re-raise on unexpected errors (diff.patch:113-114) is the correct pattern — narrow handling for parse/structure errors, propagate everything else.

## Cross-PR interaction

- Same file (`scripts/resolve-compose-stack.sh`) as #1029 (resolver gpu_backends sweep). PR body confirms mechanical conflict; rebase required.
- No other PR overlaps this file.

## Trace

- `scripts/resolve-compose-stack.sh:140-145` — yaml hoist
- `scripts/resolve-compose-stack.sh:170-172, 250-257` — empty-manifest isinstance guards
- `scripts/resolve-compose-stack.sh:233-296` — aligned user-ext loop (compose_file/.disabled/local/multigpu overlays)
