# PR #1028 — Verdict

> **Title:** fix(embeddings): raise healthcheck start_period from 120s to 600s
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/embeddings-start-period`
> **Diff:** +1 / -1 across 1 file(s) · **Risk tier: Trivial (score 0/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1028

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

**MERGE.** One-line healthcheck tuning at `extensions/services/embeddings/compose.yaml:28` raising `start_period` from 120s to 600s. Per `upstream-context.md` §8, `start_period` is healthcheck grace, not retry logic — extending it is explicitly fine ("that's not retry, that's giving slow startup more headroom"). Justified by the Hugging Face TEI image's first-start model download (~115 MB for `BAAI/bge-base-en-v1.5`) which can exceed the prior 270s total grace on slow connections. No restart-loop masking risk: Docker still triggers `restart: unless-stopped` on non-zero exit.

## Findings

- This is genuinely trivial. No code path changes, no env changes, no new files. Pure compose-yaml tuning with documented justification.
- Convention-clean: no `2>/dev/null`, no retry/fallback logic, no schema impact.

## Cross-PR interaction

- No file overlap with other open PRs in this batch. Disjoint from the host-agent and dashboard-api clusters.
- Per `analysis/dependency-graph.md`, this is part of the loosely-coupled "extension fixes" group (#1027, #1028, #1029, #1032, #1033, #1034) that could optionally collapse into a single sweep PR.

## Trace

- `extensions/services/embeddings/compose.yaml:28` — `start_period: 120s` → `600s`
