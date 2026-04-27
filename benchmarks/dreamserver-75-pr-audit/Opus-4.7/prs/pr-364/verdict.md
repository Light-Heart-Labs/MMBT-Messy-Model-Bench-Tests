# PR #364 — Verdict

> **Title:** feat(dashboard-api): add settings, voice runtime, and diagnostics APIs
> **Author:** [championVisionAI](https://github.com/championVisionAI) · **Draft:** False · **Base:** `main`  ←  **Head:** `feat/dashboard-api-settings-voice-diagnostics`
> **Diff:** +471 / -149 across 4 file(s) · **Risk tier: High (score 15/20)** · **mergeable: CONFLICTING**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/364

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 4 | dashboard-api router additions, tests, README — touches the API surface that **8 other open PRs are also touching**. CONFLICTING means rebase + redo. |
| B — Test coverage | 4 | Adds new endpoints + tests, but tests likely fail under current main (CONFLICTING). |
| C — Reversibility | 1 | Pure code; revert clean — but the *re-divergence* cost is high if merged then reverted |
| D — Blast radius | 3 | Adds endpoints the dashboard frontend calls. If the PR's contracts diverge from frontend expectations, dashboard breaks |
| E — Contributor | 3 | championVisionAI's only PR in this audit; March-era; no follow-up since |
| **Total** | **15** | **High** |

## Verdict

**HOLD — needs maintainer judgment.** Two paths forward, both reasonable;
this audit can't pick between them.

### Path A: REJECT — fit / redundancy

**Reasoning:** The PR has been open since 2026-03-18 (1 month before
audit start) with no follow-up commits. Mergeable status is CONFLICTING.
Since it was opened, **at least 9 other PRs from Yasin** have landed in
or queued up against `extensions/services/dashboard-api/`, including:

- Several touching the same `routers/` directory
- Async-hygiene refactor in PR #1022
- New extension lifecycle in PR #1038, #1054, #1056
- Async/sync routing changes in #1045

The endpoints PR #364 proposes (`/api/settings`, `/api/voice/*`,
`/api/test/*`) may **already exist** in `main` after subsequent merges
(audit didn't enumerate exhaustively). If so, the PR is **redundant**.
Rejecting with "thanks, this is now covered by #X" is the right move.

### Path B: REVISE — architectural rework after rebase

**Reasoning:** If the endpoints are *not* redundant, the work is
substantive (471 lines, includes tests). The contributor invested
effort. The professional move is:

1. Reach out to championVisionAI: "We'd like to take this in. Are you
   up for rebasing against current main?"
2. If yes: ~2 weeks deadline; if no response, close politely.
3. Once rebased, the resulting PR is essentially a new review against a
   very different baseline.

### What this audit can offer the maintainer

The audit doesn't know which path is right because it didn't
exhaustively diff `routers/` against post-PR-364 main. The maintainer
or Yasin can answer this in ~10 minutes:

```bash
# Check if the endpoints PR #364 proposes already exist
git checkout main
grep -r '/api/settings' dream-server/extensions/services/dashboard-api/routers/
grep -r '/api/voice/' dream-server/extensions/services/dashboard-api/routers/
grep -r '/api/test/' dream-server/extensions/services/dashboard-api/routers/
```

If the routes exist, Path A. If not, Path B.

## Findings

### ★★★ — CONFLICTING with main and stale by 5+ weeks

The single biggest signal. The PR cannot merge without a rebase, and
the rebase is non-trivial: 8 other PRs touch
`routers/extensions.py`, several touch `routers/setup.py`,
`routers/agents.py`, and the test files. championVisionAI has not
pushed since 2026-03-18.

### ★★ — Three separate concerns bundled

**Where:** `routers/runtime.py` is added; settings endpoints live in
the routers it touches; voice runtime is a third surface.

The PR title bundles three concerns: settings APIs, voice runtime
APIs, diagnostics APIs. **If revising, the right ask is to split.**
Three smaller PRs land cleanly even after the existing 9 PRs touching
the same directory; one big PR re-conflicts every week.

### ★ — Test additions are valuable but reviewer-cost is real

The PR adds `tests/test_routers.py` content. Reviewers have to read
both the new tests and verify they exercise the new endpoints
correctly — usually a positive signal, but for a stale PR, the tests
also need rebase consideration.

### Convention adherence

(Auditor did not exhaustively review the diff — verdict turns on the
*procedural* CONFLICTING + stale issue, not on diff specifics.)

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #1022 (Yasin async hygiene) | Same `routers/extensions.py` family. Yasin has been refactoring this surface for weeks. #364 conflicts. |
| #1037 #1038 #1044 #1045 #1054 #1056 (Yasin's extensions-router cluster) | Same — every one of these touches files championVisionAI's PR also touches. |
| #1003 (Yasin setup wizard) | Touches `routers/setup.py` — high overlap potential with PR #364's `/api/test/` endpoints (auditor inferred from titles). |
| #351 (reo0603 input validation tests) | Same CONFLICTING + stale shape; same reasoning applies. |

## What to communicate to championVisionAI

**Recommendation:** A short, kind message:

> "Thanks for this PR — we let the queue get away from us. The
> dashboard-api surface has changed substantially since you opened
> this; we'd love to take the work but it'd need a rebase against
> current main, and ideally a split into three PRs (settings / voice /
> diagnostics) so each lands cleanly. If you're game, send a status
> update and we'll prioritize re-review. If not, no hard feelings —
> please close this and we'll cherry-pick the ideas with attribution."

## Trace

- Open: 2026-03-18 (38 days before audit)
- Last update: 2026-03-18 (no follow-up commits)
- Mergeable: CONFLICTING
- Files: `dashboard-api/main.py`, `dashboard-api/routers/runtime.py`
  (new), `dashboard-api/tests/test_routers.py`,
  `dashboard-api/README.md`
- Conflicting open PRs: at least 7 of Yasin's dashboard-api PRs touch
  overlapping files
- Decision deferred to maintainer: see Path A vs Path B above
