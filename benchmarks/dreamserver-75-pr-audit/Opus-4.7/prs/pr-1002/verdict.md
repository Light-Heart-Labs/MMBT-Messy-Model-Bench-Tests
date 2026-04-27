# PR #1002 — Verdict

> **Title:** refactor(dream-cli): enable set -u and add guards for conditional variables
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `refactor/dream-cli-nounset-audit`
> **Diff:** +51 / -22 across 1 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1002

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

**MERGE — but only after PRs #1008 and #998 land.** This is the last link in Yasin's strict-mode chain: `set -eo pipefail` → `set -euo pipefail` at line 6, plus six `${VAR:-}` guards at sites that legitimately read potentially-unset variables (`SERVICE_DEPENDS[$id]:-` for missing-manifest extensions; bare `$2`/`$3` in `cmd_preset diff`; `ext1[$key]:-` and `env1[$key]:-` for sparse-associative-array iteration; `env_dir` `error "Unknown service"` short-circuit). The PR body is candid that the diff currently shares 6+ hunks with PR #998 because the branches share a base; once #998 merges, those duplicates drop out and only the unique `-u` work remains. **Cannot merge before #998 because the shared hunks would three-way conflict.**

## Findings

- **The audit methodology is the right one.** The body lists three latent bugs `set -u` would catch immediately: bare `$2`/`$3` crash in `preset diff` with no args; `ext1[$key]` / `env1[$key]` AA-read crash for keys present in only one preset; `SERVICE_DEPENDS[$id]` crash on user-extensions with malformed manifest. End-to-end testing on ~25 read-only subcommands is the right validation pass.
- **Convention adherence:** `set -euo pipefail` matches CLAUDE.md verbatim. The guards added are scoped (`${VAR:-}` — empty-string default), not catch-all (`${VAR:-something_unrelated}`). Correct discipline.
- **The DRAFT status is a deliberate merge-order safeguard**, per the body. This is good operator hygiene — Yasin is keeping the PR un-mergeable so the chain stays linear.

## Cross-PR interaction

- **Hard dependency on PR #998 (which has hard dependency on #1008).** Chain: `#1008 (READY) → #998 (DRAFT) → #1002 (DRAFT, this)`. Per the body, "after #998 merges, the operator must rebase this branch onto post-#998 main; the shared hunks drop out automatically."
- Cluster 1 conflict file (`dream-cli`). Last in the merge order per `analysis/dependency-graph.md`.
- Heavy textual overlap with #998 today; no overlap once that PR lands.

## Trace

- `dream-server/dream-cli:6` — `set -eo pipefail` → `set -euo pipefail` (the unique `-u` add over #998's `-eo`).
- `dream-server/dream-cli:1492` — `${SERVICE_DEPENDS[$service_id]}` → `${SERVICE_DEPENDS[$service_id]:-}`.
- `dream-server/dream-cli:1956-1957` — bare `$2` / `$3` → `${2:-}` / `${3:-}` in `cmd_preset diff`.
- `dream-server/dream-cli:1996, 2041, 2046-2047` — sparse-AA read sites guarded with `:-`.
- All six guard sites are append-only `:-` additions; behavior under sparse maps changes from "crash under `-u`" to "treat as empty string."
