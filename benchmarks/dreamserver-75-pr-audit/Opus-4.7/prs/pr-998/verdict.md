# PR #998 — Verdict

> **Title:** fix(dream-cli): pipefail + surface LLM failures + exit-code contract
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `fix/dream-cli-pipefail-exit-codes`
> **Diff:** +44 / -15 across 1 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/998

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **4** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE — but only after PR #1008 lands.** This is a substantive correctness fix for `dream-cli`'s error contract: `set -e` → `set -eo pipefail` at line 6, `dream chat` and `dream benchmark` now actually detect LLM failure (preflight `curl --silent --show-error --fail --max-time 3` against `/v1/models` + strict `jq -er '.choices[0].message.content'` instead of `jq -r '... // "Error: no response"'` which silently masked the failure as a string), and `cmd_disable` / `cmd_agent logs` / `_gpu_reassign` get correct non-zero exit codes for skip/failure. **Yasin's own PR description correctly identifies the merge gate**: enabling `pipefail` here makes seven existing `grep '^KEY=' .env | cut | tr` pipelines hard-exit when the key is absent. PR #1008 appends `|| true` to those seven sites — so #1008 must merge first or `dream update` / `dream rollback` / `dream enable` will abort mid-flow on installs with sparse `.env`.

## Findings

- **`set -eo pipefail` adoption matches CLAUDE.md.** The project's coding standard explicitly says `set -euo pipefail` everywhere. This PR adds two of the three flags; #1002 (also in this batch, also DRAFT) adds `-u`. Correct staging.
- **The `dream chat` rewrite is the load-bearing correctness improvement.** Pre-PR: `curl -s ... | jq -r '.choices[0].message.content // .error.message // "Error: no response"'` — `curl -s` suppresses both transport errors and HTTP errors, then `jq -r` with a string fallback prints `"Error: no response"` on stdout and exits 0. `dream benchmark` then reports sub-second "Excellent" performance against a dead backend. Post-PR: a `--silent --show-error --fail --max-time 3` preflight catches transport failures; the main chat call uses `--silent --show-error --max-time 30` (deliberately omits `--fail` so HTTP 4xx/5xx flow through to the existing `jq -er '.error.message'` fallback for actionable error text — and the comment explains the curl-7.76 compatibility reason). This is a careful, deliberate rewrite, not a sweep.
- **`sed -n '1p'` for the two `head -1` swaps is correct under pipefail.** `head -1` exits 0 then closes its stdin; with `pipefail` and a slow upstream, the upstream then SIGPIPE-aborts and the pipeline reports failure. `sed -n '1p'` reads the entire stream so the upstream sees normal EOF. Standard idiom.

## Cross-PR interaction

- **Hard dependency on PR #1008.** Body explicitly states this. #1008 is "READY" per the body's chain status; this PR is intentionally `isDraft: true` until #1008 merges.
- Cluster 1 conflict file (`dream-cli`) — overlaps with #993, #994, #997, #999, #1000. Per `analysis/dependency-graph.md`, the merge order is `#1006 → #1007 → #1008 → #993 → #994 → #997 → #1000 → #999 → #998 → #1002`. This PR sits late in the chain.
- **Heavy hunk overlap with PR #1002 (DRAFT, `set -u` follow-up).** The PR body acknowledges 6+ shared hunks. #1002 must rebase after this lands; the shared hunks then drop out and only the `-u` work remains.

## Trace

- `dream-server/dream-cli:6` — `set -e` → `set -eo pipefail` (the foundation).
- `dream-server/dream-cli:1148-1185` — `cmd_chat` rewrite with preflight + strict `jq -er` + delegated 4xx/5xx error path.
- `dream-server/dream-cli:1198-1200` — `cmd_benchmark` aborts on `cmd_chat` failure (was: `2>/dev/null` swallow + 0 exit).
- `dream-server/dream-cli:1550, 2492, 2855, 2870, 2873, 2874` — exit-code contract fixes (`return 1` instead of `return`).
- `dream-server/dream-cli:254, 1923` — `head -1` → `sed -n '1p'` for SIGPIPE safety under pipefail.
