# Contributor Notes

Per-contributor patterns observed across the 75 open PRs. Useful for
calibrating review depth, deciding which contributors should be encouraged to
stack PRs, and which need more onboarding before bigger features.

## Headline distribution

| Contributor | Open PRs | Lines added | Lines removed | Pattern |
|-------------|---------:|------------:|--------------:|---------|
| Yasin Bursali (`yasinBursali`) | 63 | ~7,800 | ~1,300 | Methodical sweep of dream-cli, host-agent, dashboard-api, extensions |
| Dmytro (`boffin-dmytro`) | 3 | ~860 | ~70 | Diagnostics, audit follow-ups, docs sync |
| Y / Youness (`y-coffee-dev`) | 2 | ~3,140 | ~190 | AMD multi-GPU + installer fix |
| Arifuzzaman Joy (`Arifuzzamanjoy`) | 2 | ~5,080 | ~170 | Vast.ai p2p-gpu + compose env defaults |
| Pheonix DEV (`reo0603`) | 1 | ~370 | ~2 | Input validation tests (stale) |
| championVisionAI | 1 | ~470 | ~150 | Dashboard-api settings/voice/diagnostics (stale) |
| Gabriel (`gabsprogrammer`) | 1 | ~6,890 | ~26 | Mobile (Termux + a-Shell) |
| Dependabot | 2 | ~9 | ~9 | Action version bumps |

## Yasin Bursali — 63 of 75 PRs

**Background per memory:** Mac/full-stack contributor. Established core
contributor with deep familiarity of the codebase.

**Pattern in this batch:** A *methodical, breadth-first sweep* across the
codebase. Each PR is small-to-medium, focused on one concern, and almost
always correct in isolation. Subsystems touched (in PR-count order):

1. `dream-cli` — 14 PRs (mostly bug fixes and Apple Silicon coverage)
2. `dashboard-api` — 11 PRs (async hygiene, async + lifecycle, new endpoints)
3. `host-agent` — 8 PRs (security, install flow, runtime hygiene, retry)
4. `extensions` — 7 PRs (manifest fixes, healthcheck tuning, dependency mirroring)
5. `installer-macos` / `installer-windows` — 6 PRs (cross-platform polish)
6. `dashboard-ui` — 4 PRs (template picker, error handling)
7. Tests — 5 PRs (mostly draft, BATS coverage)
8. Docs — 3 PRs (post-merge sync, security)
9. CI / chore — multiple

**What's working:**
- Conventional Commits format used throughout
- One concern per PR
- Bodies usually explain *why*, not just *what*
- Very low contributor-axis risk; PRs adhere to project conventions

**What's not working as well:**
- **Single-PR-per-fix means heavy file overlap** — 14 PRs touch
  `dream-cli`, 8 touch `routers/extensions.py`, 7 touch host-agent. Merging
  them serially is cheap individually but creates 13 conflict resolutions
  in aggregate.
- **Drafts left as drafts** — 15 of his PRs are in draft state, several
  for architectural-cleanup work that arguably belongs together with the
  non-draft PRs.
- **No explicit ordering** — PRs that depend on each other (e.g. #1017's
  title literally says "post-#988") aren't ordered explicitly via the
  base branch. Reviewers have to deduce.

**Recommendation to maintainer:**
- Establish a stack-PR convention with Yasin: when 5+ PRs target the same
  file, ask for a single tracking issue and a stack of dependent branches
  rather than parallel PRs. Reduces merge-conflict toil for both sides.
- Encourage him to mark drafts as "ready" or close them. The draft set
  appears to be exploratory; explicit signals make triage easier.
- Yasin's PRs are the lowest-risk contributor-axis-wise. Do NOT add
  friction here — these are net-positive sweeps, just with an org problem.

## Y / Youness (`y-coffee-dev`) — 2 PRs

**Background per memory:** "Y/Youness on multi-GPU."

**PRs:**
- **#750** — `feat: AMD Multi-GPU Support` — 5,054 additions / 165 deletions, 33 files. The flagship multi-GPU work; touches `dream-cli`, `.env.schema.json`, AMD config files, and adds AMD-specific GPU detection logic.
- **#1043** — `fix(installer): custom menu's 'n' answers were not actually disabling services` — 47 additions / 47 deletions. Bug fix in feature-selection menu logic.

**Pattern:** Specialist on multi-GPU AMD work. PR #750 is a major feature
that impacts the AMD developer-program partnership. PR #1043 is a small,
unrelated bug fix that shows familiarity with the installer flow.

**Risk note:** #750 touches hardware-specific code that we can't run on
this audit's available environments. Verdict relies on diff inspection plus
reading the relevant `installers/lib/` code. We **explicitly cannot
verify** the multi-GPU detection works on real Strix Halo / multi-7900-XTX
hardware. Recommend the maintainer do that before merging.

**Recommendation:** PR #1043 is an easy merge. PR #750 is a "test on real
AMD hardware before merge" — likely needs a session with Y on a real rig.

## Dmytro (`boffin-dmytro`) — 3 PRs

**PRs:**
- **#1042** — `feat(support): add redacted diagnostics bundle generator` — 796 additions, 3 files. New diagnostics-bundle feature.
- **#966** — `docs(platform): sync Windows and macOS support docs` — 44/30, 1 file. Docs sync.
- **#959** — `fix: address audit findings — Windows docs, Token Spy auth, and incubator disclaimers` — 23/9, 3 files. Audit follow-ups.

**Pattern:** Documentation, audit follow-up, observability tooling. The
support-bundle PR (#1042) is a substantive add — it's the kind of feature
the maintainer should be able to point users to when they file bugs ("run
`dream support` and attach the JSON"). Worth merging.

**Recommendation:** All three are merge-candidates after small review.
#1042 is the highest-value of the three.

## Arifuzzaman Joy (`Arifuzzamanjoy`) — 2 PRs

**PRs:**
- **#983** — `feat(resources): add p2p-gpu deploy toolkit for Vast.ai` — 5,054 additions / 165 deletions, 33 files.
- **#716** — `fix(extensions-library): add sensible defaults for required env vars` — 27/4, 3 files. Note this PR's `baseRefName` is `resources/dev`, not `main`.

**Pattern:** Bounty contributor (per the maintainer's bounty memo).
Substantial features but the framing raises **fit** questions.

**Risk note:** #983 (Vast.ai cloud deploy) potentially conflicts with
DreamServer's "no cloud" positioning. Even though the PR adds resources/,
not core, it's worth a maintainer judgment call. See `prs/pr-983/verdict.md`.

#716 is small, clean, and against `resources/dev` — its base branch
suggests the contributor knows about the resources/ workflow. This is a
good signal of contributor track record despite limited prior PRs.

## Pheonix DEV (`reo0603`) — 1 PR (#351)

**PR:** `test: add comprehensive input validation and injection resistance tests` — 370/2, 5 files.

**Pattern:** Stale March-era PR, currently CONFLICTING. Substantive test
addition (5 files of pytest); merit is real but the rebase will be
non-trivial after ~70 PRs landed since.

**Recommendation:** Reach out to confirm contributor still wants the PR in;
if yes, revise after rebase; if no response in 2 weeks, close politely.

## championVisionAI — 1 PR (#364)

**PR:** `feat(dashboard-api): add settings, voice runtime, and diagnostics APIs` — 470/149, 4 files.

**Pattern:** March-era PR, CONFLICTING, 4 CI failures, no recent activity.
Touches the dashboard-api routers — a hot-spot now (8 other PRs since).
Substantial conflict resolution needed.

**Recommendation:** Same as #351 — reach out, deadline, otherwise close.

## Gabriel (`gabsprogrammer`) — 1 PR (#961)

**PR:** `feat: add mobile paths for Android Termux and iOS a-Shell` — 6,891/26, 30 files.

**Pattern:** First-PR contributor with a *very* large mobile-platform
addition. Mobile is not on the documented roadmap — this PR is essentially
asking the project to add a new platform target. The size (6,891 lines) is
the second-largest in the queue.

**Recommendation:** **HOLD — needs maintainer judgment.** Two real
questions for Michael:
1. Is mobile (Termux + a-Shell) on the roadmap? If no, the answer to the
   PR is "thanks, not now". If yes, the answer is "yes, but can we land
   it in stages — start with Termux only?".
2. The contributor's experience level with the codebase is unproven; a
   30-file addition from a first-PR contributor is the highest-risk
   shape in the queue.

This is the verdict that takes longest to write because it depends on
your strategic answer, not a code question.

## Dependabot — 2 PRs

**PRs:**
- **#990** — `chore(deps): bump actions/github-script from 8.0.0 to 9.0.0`
- **#991** — `chore(deps): bump anthropics/claude-code-action from 1.0.97 to 1.0.104`

**Pattern:** Standard. CI-failing on the same `integration-smoke` regression
as everything else; otherwise green. Auto-merge candidates after the BATS
fix.

## Bounty-tier alignment

The brief notes the bounty system: $40 (Small), $150 (Medium), $400
(Large). Inferring tier from PR scope (no explicit labels in metadata):

| Probable tier | PRs | Rationale |
|--------------|-----|-----------|
| Small | Most of Yasin's bug fixes (40+ PRs) | Single-file, single-concern fixes |
| Medium | #1042 (support bundle), #1003 (setup wizard sentinel), #988 (loopback) | Multi-file, defined scope |
| Large | #750 (AMD Multi-GPU), #364 (dashboard-api APIs), #961 (mobile), #983 (p2p-gpu), #1018+#1019+#1020 (test stack) | Multi-system, substantial design effort |

**No tier mismatches detected** that warrant a flag — the PR scopes look
roughly proportional to the work involved.
