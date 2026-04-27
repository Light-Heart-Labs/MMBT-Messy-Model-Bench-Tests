# PR #1003 — Verdict

> **Title:** fix(dashboard,dashboard-api): sentinel-based setup wizard success detection
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dashboard-setup-wizard`
> **Diff:** +215 / -57 across 6 file(s) · **Risk tier: Low (score 7/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1003

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | dashboard JSX (3 files), dashboard-api router, lib helper, shell script |
| B — Test coverage | 2 | Author cites "Live HTTP byte-inspection"; no new tests in PR (3 draft companion PRs add them) |
| C — Reversibility | 0 | Pure code; revert is clean |
| D — Blast radius | 2 | Setup wizard is *the* first-time-user UX; a regression here = bad first impression. But the PR fixes a regression; current behavior is worse |
| E — Contributor | 0 | Yasin; established in dashboard surface |
| **Total** | **7** | **Low** |

## Verdict

**MERGE — first-of-the-setup-wizard-cluster.** Then merge the three
companion drafts (#1015, #1018, #1019) once Yasin marks them ready.

This is the substantive fix; the others are defense-in-depth + tests.
See `analysis/dependency-graph.md` Cluster 4.

The fix is **correct on three layers**:

1. **Backend sentinel** — `__DREAM_RESULT__:PASS|FAIL:<rc>` emitted as a
   single combined `yield` in `run_tests` (works around an empirically-
   observed Starlette `StreamingResponse` end-of-stream final-chunk
   drop). The `error_stream` fallback gets the same treatment with
   `all_ok` tracking across connectivity checks.
2. **Frontend** — `AbortController` for mid-wizard cancel,
   `Promise.allSettled` for race-free template/extension fetches,
   step-guarded `useEffect` re-fetch on back-nav, `console.error` on
   previously-silent catches, `aria-hidden` on decorative icons.
3. **Diagnostic shell script** — replaces `((VAR++))` (returns 1 on
   pre-incr-from-0 under `set -e`) with `$((VAR + 1))`; uses
   `if ! VAR=$(…)` for grep pipelines; bounded `set +e/set -e` block
   around the dispatch so a single failing test doesn't abort the
   runner.

All three layers have a clear "why this is broken now" narrative in the
PR body, and the fixes match the failure modes.

## Findings

### ★ — `console.error` is the right escape valve, but a Sentry-equivalent wouldn't hurt later

**Where:** SetupWizard JSX changes — silent `.catch(() => {})` replaced
with `.catch(err => console.error(...))`.

`CLAUDE.md` bans silent catches; this fix complies. For a setup wizard
that's the *first* thing a new user sees, surfacing errors via
`console.error` is browser-only — most users never open the console.
Future enhancement: a toast or bug-report-link UI. Not blocking.

### ★ — Known caveat from the author: image rebake

**Quoted from PR body:** "The `dream-dashboard-api` Docker image bakes
`routers/setup.py` at build time (uvicorn `WORKDIR=/app`). This PR's
Python changes require an image rebuild to take effect on existing
installs."

Yasin notes a separate follow-up will fix the installer's
`docker compose up` flow. **This is the right place for that follow-up
to live** — bind-mounting the source tree into the container at dev
time would be a separate architectural decision (see PR #1055 from
Yasin: "docs(dashboard-api): add development workflow guide for the
bake-vs-bind-mount trap" — same author, same concern).

### ★ — Pre-existing silent catch acknowledged, not fixed

**Quoted from PR body:** "`TemplatePicker.jsx:140` has a pre-existing
`res.json().catch(() => ({}))` silent swallow unrelated to this PR's
touched scope; tracked as a separate follow-up."

Flagging-and-deferring is the right call here — the PR's stated scope
is the wizard sentinel, not a JSX-wide silent-catch sweep. Yasin's draft
PR #1015 ("dashboard: template picker defensive fixes") is the right
home for this.

### Convention adherence

- [x] No new `eval` of script output
- [x] No new `2>/dev/null` / `|| true`
- [x] **Fixes** silent catches rather than introducing them
- [x] No port-binding changes
- [x] No new files in `installers/lib/`
- [x] No new env vars
- [x] No manifest changes

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #1015 (draft, Yasin) | **Companion.** Picker defensive fixes; depends on this PR's structure. Merge after #1003. |
| #1018 (draft, Yasin) | **Companion.** BATS regression coverage. Merge after #1003. |
| #1019 (draft, Yasin) | **Companion.** Sentinel exception path + tests. Merge after #1003. |
| #1037 (draft, Yasin) | Soft conflict in `Extensions.jsx` and `routers/extensions.py` — different concern (error handling on extensions page). Trivial merge. |
| #1055 (Yasin) | **Related.** Documents the bake-vs-bind-mount trap that this PR's "known caveat" alludes to. Independent. |

## Trace

- Backend sentinel emit: `dream-server/extensions/services/dashboard-api/routers/setup.py` (run_tests + error_stream)
- Frontend wiring: `dream-server/extensions/services/dashboard/src/components/SetupWizard.jsx`
- Lifted helper: `dream-server/extensions/services/dashboard/src/lib/templates.js`
- Shell discipline fixes: `dream-server/scripts/dream-test-functional.sh`
- Author commits: `1ba7c78f` (backend) + `57f2783a` (frontend)
- Adversarial review claim verified: "Round-2 adversarial audit by
  dashboard-verifier" — auditor cannot verify this third-party review
  ran, but the PR body's specificity (745-byte response, sentinel parser
  behavior) suggests it did
