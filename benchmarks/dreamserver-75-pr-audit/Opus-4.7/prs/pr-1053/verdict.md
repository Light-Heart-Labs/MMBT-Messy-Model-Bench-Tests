# PR #1053 — Verdict

> **Title:** ci(openclaw): filesystem-write gate to detect new openclaw write paths
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `ci/openclaw-docker-diff-gate`
> **Diff:** +131 / -0 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1053

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE** (after #1035, per draft note)

CI-only gate, root-level (no production blast radius). The pivot from `docker diff` (which can't see writes into volumes) to a host bind-mount audit (diff.patch:84-88) is the right call — the original issue's `docker diff | grep` would have always passed false-green. Workflow correctly scopes triggers via paths-filter (diff.patch:30-33), uses minimal `permissions: contents: read` (diff.patch:35-36), pins image tag matching `compose.yaml` (`ghcr.io/openclaw/openclaw:2026.3.8`, diff.patch:43), and includes both negative (find of unexpected files, diff.patch:117-127) and positive (`openclaw.json` presence, diff.patch:131-134) assertions. The positive check guards against silent-crash false-greens — exactly the right level of paranoia for an audit gate.

## Findings

- `set -euo pipefail` set in each `run: |` block. `|| true` only on cleanup `docker rm -f` (diff.patch:108) and `tail -100` (diff.patch:99) — both are best-effort, post-failure paths. Within project conventions.
- The 4-line NOTE at diff.patch:73-77 about deliberately omitting `OPENCLAW_CONFIG_PATH` is good defensive documentation against future "fixers."
- 30s `sleep` (diff.patch:91) is tuned to startup writes; reasonable for a one-shot audit.

## Cross-PR interaction

- No file overlaps with any open PR.
- Semantically depends on #1035 (simplified openclaw volume layout) for the gate to be meaningful. Until #1035, named volumes can swallow the writes the gate wants to audit. Draft label + must-merge-after #1035 is the correct safeguard.

## Trace

- `.github/workflows/openclaw-image-diff.yml:1-131` — new workflow with paths-filter scope, bind-mount audit mechanism, and false-green guards
