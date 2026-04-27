# PR #1029 — Verdict

> **Title:** fix(resolver): dedupe override.yml; apply gpu_backends filter to user-extensions
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/compose-resolver-dedup-gpu-filter`
> **Diff:** +46 / -7 across 2 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1029

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

**MERGE.** Two correct fixes in one tight PR. (1) `installers/lib/compose-select.sh:102-108` was double-appending `docker-compose.override.yml` because the upstream resolver already includes it — the deletion is right and side-steps anchor/extends/list-merge ambiguity. (2) `scripts/resolve-compose-stack.sh:223-275` mirrors the built-in extension's `gpu_backends` filter to the user-extension loop, fixing the case where a `gpu_backends: [nvidia]` user extension was being merged on AMD/Apple. The broad-`except` block at `:248-260` is a deliberate dispatch that re-raises non-yaml/json/structure errors — matches the project's "narrow exceptions at I/O boundaries" rule (`upstream-context.md` §8).

## Findings

- **Lib purity unchanged or improved:** the `compose-select.sh` change *removes* code from lib. No new I/O introduced. Aligns with `upstream-context.md` §3.
- **Filter logic is identical to the built-in loop** verbatim — same default `["amd","nvidia"]`, same `"all"`/`"none"` sentinels, same suffix preference order, same `skip_broken` honoring. Important for consistency between core and user extensions.
- **Scope limit is honest:** PR body explicitly notes user-extension loop still hardcodes `compose.yaml` and skips `compose.local.yaml`/`compose.multigpu.yaml` overlays. That's a pre-existing gap, deliberately deferred.
- **Re-raise pattern at `:271-272`** prevents silent swallowing of programmer errors — a `KeyError` on `.get(...)` would never trigger (uses `.get()` defaults), but anything outside the dispatch tuple propagates.

## Cross-PR interaction

- No file overlap with other open PRs in this batch — `compose-select.sh` and `resolve-compose-stack.sh` aren't touched by host-agent or extensions.py clusters.
- Related to the disjoint extension-fixes group (#1027/#1028/#1029/#1032/#1033/#1034) — could collapse into a single sweep if the maintainer wants.

## Trace

- `installers/lib/compose-select.sh:102-108` — duplicate `override.yml` append removed
- `scripts/resolve-compose-stack.sh:226-231` — yaml availability probe (mirrors built-in)
- `scripts/resolve-compose-stack.sh:236-247` — manifest discovery + schema gate + `gpu_backends` filter
- `scripts/resolve-compose-stack.sh:248-272` — exception dispatch with re-raise for unknown types
