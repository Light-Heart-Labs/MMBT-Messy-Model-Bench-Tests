# PR #1000 — Verdict

> **Title:** feat(dream-cli): --json flag on list/status and document doctor --json
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `feat/dream-cli-json-flag`
> **Diff:** +53 / -6 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1000

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

**MERGE.** Two correct fixes plus a docs update. (1) The main case dispatch at `dream-cli:3434-3436` previously had `status|s) cmd_status ;;` and `list|ls) cmd_list ;;` with no `shift` and no `"$@"` — so any flag passed (e.g. `--json`) was silently dropped. Fixed to `shift; cmd_<x> "$@"`. (2) `cmd_status` and `cmd_list` parse `--json` and an "unknown argument" error. (3) `cmd_status --json` delegates to the existing `cmd_status_json` inside a subshell `( cmd_status_json )` to isolate that function's `RETURN` trap — without the subshell, the trap leaks into `cmd_status`'s frame and re-fires under `set -u` (which lands later via #1002). The defensive subshell is correct: it costs one fork and prevents a known crash mode.

## Findings

- **The `--json` dispatch bug was real.** Pre-PR, `dream list --json` ran the human-readable code path and exited 0 with a header table — scripts piping to `jq` got a parse error. This is the kind of "looks like it works because no error" bug that survives long enough to make it into automation tutorials.
- **The subshell wrap on `cmd_status_json` is a defensive shim, not a workaround.** The PR body is candid that the underlying RETURN-trap leak is latent in `main` today and will become a real crash when `set -u` lands. Wrapping in a subshell is the correct minimal fix at this PR's scope; the proper trap fix can land with #1002 (which adds `set -u`).
- **Convention adherence:** No `eval`, no `2>/dev/null` additions outside the existing pattern (`load_env 2>/dev/null || true` is preexisting), no port bindings, no schema changes. Single-file `dream-cli` change.

## Cross-PR interaction

- Cluster 1 conflict file. Per dependency graph, sits between #997 and #999 in merge order. Textual conflicts only.
- Touches the main case dispatch — also touched by every other Cluster-1 PR. Mechanical merge.
- Adds a sticky precedent: every other dream-cli command that accepts flags should adopt the same pattern (`shift; cmd_<x> "$@"`) — not blocking for this PR but a consistent direction.

## Trace

- `dream-server/dream-cli:518-531` — `cmd_status` `--json` parser + subshell delegation to `cmd_status_json`.
- `dream-server/dream-cli:1664-1696` — `cmd_list` `--json` parser + JSON array emit (`{id, category, status}`).
- `dream-server/dream-cli:3435, 3437` — main case dispatch fix: `shift; cmd_<x> "$@"`.
- `dream-server/dream-cli:3310-3340` — help text updated to advertise `--json` flags.
