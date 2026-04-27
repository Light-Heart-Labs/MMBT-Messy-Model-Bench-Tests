# PR #1006 — Verdict

> **Title:** fix(dream-cli): route log() and warn() to stderr so command captures remain clean
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dream-cli-log-to-stderr`
> **Diff:** +2 / -2 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1006

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE — first in the dream-cli stack.** Appends `>&2` to `log()` and `warn()`
at `dream-cli:45,47`. This is the foundation fix the dependency graph
identifies as the head of the dream-cli cleanup chain — every downstream PR
(#993 colors, #998 pipefail, #1008 grep guards, etc.) inherits this stderr
routing. The motivating bug is real: `cmd_benchmark`'s `$(cmd_chat ...)` capture
at `dream-cli:1174` uses `2>/dev/null`, so the
`[dream] Sending to <model>...` line currently leaks into the `Response:`
output. Routing log to stderr cleanly separates status from data and matches
Unix convention. JSON-emitting paths (`cmd_status_json`, `cmd_doctor --json`)
do not call `log`/`warn` before emitting, so machine output is unchanged.

## Findings

- Scope is intentionally minimal: only `log()` and `warn()` move; `success()`,
  `error()`, and `log_warn()` stay on stdout. That preserves the existing
  contract that errors and successes are still terminal-visible without `2>&1`.
- The body's claim that no script/test captures `dream-cli` stdout expecting
  `[dream]` or warning prefixes is the right invariant to verify. Diff is
  small enough that any silent breakage would manifest as a test regression
  immediately.
- This is the foundation for the dream-cli stack. Bug fixes (#1007, #1008)
  and feature work (#999, #1000) all assume log() goes to stderr. Land first.

## Cross-PR interaction

- Textually conflicts with every other dream-cli PR (#993, #994, #997-1000,
  #1002, #1007, #1008, #1011, #1016, #1018, #1020). Per `analysis/dependency-graph.md`,
  this PR is the recommended first merge in that stack — downstream PRs rebase
  cleanly afterward.

## Trace

- `dream-server/dream-cli:45` — `log()` adds `>&2`
- `dream-server/dream-cli:47` — `warn()` adds `>&2`
- `dream-server/dream-cli:1174` — `cmd_benchmark` capture (the motivating site)
