# PR #1054 — Verdict

> **Title:** fix(dashboard-api): require deployable compose.yaml to mark extension installable
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/catalog-installable-requires-compose`
> **Diff:** +4 / -1 across 1 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1054

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

**MERGE**

Three-line predicate tightening that removes a real UX trap. `_is_installable` previously returned True for any library directory; dify and jan ship only `compose.yaml.disabled`, fooocus only `.reference` files, so clicking Install copied them and then failed cryptically because no compose was deployable. The fix at diff.patch:9-13 adds the missing `(ext_dir / "compose.yaml").exists()` clause. aider intentionally retains a real `compose.yaml` (per PR body) so it stays installable. No schema changes, no signature changes, no frontend changes — just the boolean flips for the three broken entries.

## Findings

- The predicate hardcodes filename `compose.yaml` (diff.patch:13). The PR body acknowledges this as load-bearing on the current convention. Acceptable; future extensions with non-standard `compose_file` would need separate handling.
- 137 dashboard-api tests pass per PR body — change is in a hot-path predicate, regression risk on the catalog endpoint is low.

## Cross-PR interaction

- Per dependency graph: `#1022 → #1054 → #1044 → #1056 → #1038 → #1045 → #1037`. This is upstream of #1056/#1045/etc; touches a different function (`_is_installable`) than those PRs.
- No file overlaps with other yasinBursali batch PRs at the function level.

## Trace

- `extensions/services/dashboard-api/routers/extensions.py:212-218` — `_is_installable` now requires `compose.yaml` on disk
