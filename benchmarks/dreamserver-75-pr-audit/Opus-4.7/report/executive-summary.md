# Executive Summary

> **For:** Michael Bradley, Dream Server maintainer
> **Audit:** 75 open PRs against [Light-Heart-Labs/DreamServer](https://github.com/Light-Heart-Labs/DreamServer) at baseline `d5154c3`
> **Audit completed:** 2026-04-27 (~5 hours real time)
> **Audit horsepower:** Claude Opus 4.7 (1M context) on the maintainer's Windows workstation
> **Read:** This file (3 pages), then [`analysis/dependency-graph.md`](../analysis/dependency-graph.md), then [`report/backlog-strategy.md`](backlog-strategy.md). Skip the per-PR directories unless you want a specific verdict.

## Headline numbers (final, all 75 PRs verdicted)

| Verdict tier | Count | Notes |
|--------------|------:|-------|
| **MERGE** clean | 51 | Most are Yasin's focused fixes; 5 are this audit's deep-dive Mediums (#988, #1003, #1042, #1043, #1050) |
| **MERGE — gated on prior PR** | 2 | #998 needs #1008 first; #1002 needs #1008 + #998 first |
| **REVISE — small** | 6 | #716, #959, #1026, #1030, #1038, #1040 — concrete diff suggestions in each verdict |
| **REVISE — architectural** | 1 | #750 (AMD Multi-GPU): address maintainer's CHANGES_REQUESTED, then merge after real-hardware verification |
| **REJECT — quality** | 1 | #351 has a committed git conflict marker in test_routers.py:111; close or have reo0603 fix |
| **HOLD — needs your judgment** | 14 | See breakdown below |

### The 14 HOLDs — three flavors

**Strategic / product (3):** #364 (stale March-era dashboard APIs — reach
out, deadline, or close), #961 (mobile Termux + iOS — roadmap question),
#983 (Vast.ai p2p-gpu — "no cloud" positioning question), #990
(dependabot actions/github-script v9 — manual grep needed for ESM
breaking change).

**Stacked-on-unmerged-deps (10):** #1015, #1016, #1017, #1018, #1019,
#1020, #1037, #1039, #1051, #1052. Every one of these has a verdict
that says "the work itself is fine; merge after dep X." They become
straight MERGEs once their parents land. See
[`analysis/dependency-graph.md`](../analysis/dependency-graph.md).

**Author-marked draft + needs review (1):** #1037 (UI defensive fixes;
overlaps heavily with #1038).

> **Net merge-ready right now: 51 clean MERGEs.**
> **After Wave 1 (BATS fix + #988): another ~10 unblock as their deps land.**
> **Final residual after dep-graph drains: ~5 PRs needing real conversations.**

## Critical findings from per-PR review (read before merging anything)

These surfaced during the per-PR diff inspection and are not visible in
PR titles or CI signals. Worth a few minutes of your attention before
the merge waves.

| # | Finding |
|---|---------|
| 1 | **PR #351 has a committed git conflict marker** at `dream-server/extensions/services/dashboard-api/tests/test_routers.py:111`. The file is unparseable Python on merge. Verdict is **REJECT — quality**; close politely or ask reo0603 to extract just the test additions onto a fresh branch. |
| 2 | **PR #1030 has a likely test bug** — `tests/test_host_agent.py:236` asserts the literal substring `"did not reach running state within 15s"` against `inspect.getsource(_handle_install)`, but the production code uses an f-string (`f"...within {startup_timeout}s..."`). The PR claims 44/44 tests passing; this assertion is suspicious. Verify before merge. |
| 3 | **PR #1026 introduces SIX new `2>/dev/null` redirects** in newly-added bash blocks (Linux Phase 13 + macOS Phase 6). Convention violation per `CLAUDE.md`. Easy fix — drop them and let stderr surface to the existing `ai_warn` else-branch. Verdict: **REVISE — small**. |
| 4 | **PR #1037 and #1038 substantially overlap.** Both add the same `unhealthy` extension status (backend + summary bucket + UI badge + filter chip + "Check Logs" button). Per `analysis/dependency-graph.md`, **merge #1038 first**, then #1037 becomes a UI-only delta. Otherwise you resolve a 100+ line conflict twice. |
| 5 | **PRs #1039, #1040, #1045 each carry duplicate `_find_ext_dir` + bind-mount filter widening + 15s state poll.** Triple-overlap in `bin/dream-host-agent.py`. Whichever lands first forces rebase on the other two. **Pick a primary** and have the other two strip the duplicates. PR #1057 takes a different angle on the same `_precreate_data_dirs` function (dict-form support). |
| 6 | **PR #1027 ships a static enforcement gate** for the BIND_ADDRESS loopback policy: `tests/test-bind-address-sweep.sh`. This *strengthens* the loopback policy from #988. Worth surfacing — it's a defense-in-depth contribution disguised as a 31-file change. |
| 7 | **PR #973 should land after #988** — its new `SECURITY.md:79-103` "Host Agent Network Binding" section documents post-#988 behavior. Same gating principle as PR #1017. |
| 8 | **PR #997 removes a `docker exec ... /bin/bash || docker exec ... /bin/sh` retry chain** (CLAUDE.md violation in pre-existing main code) and replaces it with explicit branching. **Direction-of-change positive signal.** |
| 9 | **PR #998 and #1002 share 6+ identical hunks** because branches share a base. Merge order is mechanical: **#1008 → #998 → #1002**. #1002 will rebase clean once #998 lands. |
| 10 | **PR #990 (dependabot github-script v8 → v9) is a documented breaking change** — v9 makes `@actions/github` ESM-only, so `require('@actions/github')` no longer works inside `script: \|` blocks. Five blocks need a manual grep before merge: `.github/workflows/autonomous-code-scanner.yml:1225,1260` and `.github/workflows/claude-review.yml:222,424,463`. |
| 11 | **PR #716 weakens production defaults** to fix a CI symptom. Targets `resources/dev`, not `main`. The validator-side change is correct; the compose-side change should be reverted. Verdict: **REVISE — small**. |
| 12 | **PR #1008's seven `\|\| true` patterns are intentional**, paired with downstream defensive checks. Without them, `dream update`/`rollback`/`enable`/`preset`/`dry-run` break the moment #998 (pipefail) lands. Verdict explicitly carves this out as a justified exception. |
| 13 | **PR #1046 confirmed not a #988 regression** — the 0.0.0.0 bind is container-internal (Next.js `HOSTNAME` env var); host-side mapping `${BIND_ADDRESS:-127.0.0.1}:...:3000` was untouched. **Merge OK.** |
| 14 | **PR #1047 correctly leaves `NEXTAUTH_URL` untouched** while sweeping in-container healthcheck URLs. The OAuth callback URL is browser-evaluated and must stay as the hostname users see. |
| 15 | **PR #1056 multi-concern is genuinely tied together** — catalog timeout, orphaned whitelist, GPU passthrough scan, health_port — all four are real user-extension path bugs, not scope creep. Worth flagging because the title sounds like scope creep. |

## Three things to do **before any PR merges**

### 1. Cherry-pick the 1-line BATS fix from PR #750 onto `main` first

PR #750 (AMD Multi-GPU) bundles a one-line fix to
`tests/bats-tests/docker-phase.bats:100`:

```diff
-    assert_output $'sudo\ndocker'
+    assert_output "sudo docker"
```

That single line is the **integration-smoke** failure on **72 of 75 PRs**.
Right now you cannot tell from CI status whether a PR is broken; every
red rollup is the same pre-existing assertion bug on `main`. Reproduction
script in [`testing/reproductions/repro-bats-docker-cmd-arr.sh`](../testing/reproductions/repro-bats-docker-cmd-arr.sh).

Cherry-pick to its own trivial PR. Merge directly. Five minutes; 72 PR
CI signals become trustworthy.

### 2. Merge PR #988 (loopback bind for llama-server + host agent)

[`prs/pr-988/verdict.md`](../prs/pr-988/verdict.md). Cross-platform
security fix that closes the same class of default-permissive-bind
problem `SECURITY_AUDIT.md` H3 documented (and PR #67 partially
addressed). Hard dependency for **PR #1017** which is literally titled
*"docs(security): Linux host-agent fallback is 127.0.0.1 post-#988"*.

Caveats are follow-up quality (BATS coverage, style consistency), not
blockers.

### 3. Decide the three HOLDs

Three PRs cannot be auto-verdicted — they need a maintainer-level call:

- **#961** — gabsprogrammer's mobile (Termux + iOS a-Shell), 6,891 lines,
  first PR. **Is mobile on the 2026 roadmap?** If no: reject with thanks.
  If yes: ask to split into 3 staged PRs (entry-point, Android, iOS WASM).
  Includes a binary `llama-cli.wasm` in the repo — sets a precedent.
- **#983** — Arifuzzaman's Vast.ai p2p-gpu deploy toolkit, 5,054 lines.
  Code is structurally isolated under `resources/p2p-gpu/`; cannot
  regress core. **Is "no cloud" the load-bearing brand line, or can a
  cloud-deploy *recipe* live in `resources/`?** A reasonable reading
  exists for either answer.
- **#364** — championVisionAI's dashboard-api APIs, 471 lines,
  CONFLICTING and stale by 5+ weeks. Either reject (functionality may now
  be redundant — 9 newer PRs touched the same files since) or revise
  (reach out, request rebase + split, set deadline).

Detailed reasoning in each PR's [`verdict.md`](../prs/).

## Three highest-priority MERGES (after #988)

In order:

1. **#1003** (Yasin, setup-wizard sentinel) — fixes a real first-time-
   user UX regression. The wizard previously greenlit users on a failed
   diagnostic; this PR adds machine-readable `__DREAM_RESULT__` sentinel
   plus AbortController + Promise.allSettled + step-guarded useEffect.
   Three companion drafts (#1015, #1018, #1019) follow as a stack.
2. **#1050** (Yasin, FS preflight) — blocks installs on FAT/exFAT/NTFS
   where chmod 600 on `.env` is silently a no-op. Defense-in-depth at
   runtime via host-agent. Same security class as #988.
3. **#1042** (Dmytro, support bundle generator) — high-leverage
   diagnostic tool for issue triage. Privacy-first design, redacts
   secrets, best-effort pattern. Saves time on every future bug report.

## Three highest-risk situations

1. **The dream-cli convergence** — 14 of Yasin's open PRs touch the
   45K-line `dream-server/dream-cli` Bash file. Merging in any order
   produces 13 conflict-resolutions that Yasin will own. **Recommendation:**
   ask Yasin to consolidate into a stack (`fix/cli-cleanup-q2-2026`
   parent → individual children). One merge train instead of 14.
2. **Two stale CONFLICTING PRs** (#351 `reo0603` input-validation tests,
   #364 `championVisionAI`) sit in the queue from March. Both predate
   ~70 PRs landing in adjacent files. Decide soon — outreach, deadline,
   or close.
3. **PR #750 needs real-hardware verification you have**, the audit
   doesn't. Architecture is sound, code is clean, CI is green, but the
   AMD-developer-program partnership means an AMD regression has external
   relationship costs. Verify on the 4×MI300X rig the author tested on
   (or coordinate with Y); the verdict is `REVISE — architectural rework
   per existing CHANGES_REQUESTED, then MERGE pending hardware test`.

## Dependency hot spots

The single highest-value strategic call: **decide the merge order for
the dream-cli + host-agent + extensions-router convergence**. From
[`analysis/dependency-graph.md`](../analysis/dependency-graph.md):

- **dream-cli** (15 PRs touching the same file) — recommended order:
  #1006 (stderr) → #1007 (quote tmpdir) → #1008 (pipefail grep) → #993
  (colors) → #994 (secret masking) → #997 (preflight) → #1000 (--json) →
  #999 (Apple GPU) → drafts → #1018/#1020 (tests last). #750 also
  touches this file; merge **before** the cluster.
- **host-agent** (10 PRs) — order: **#988** (security) → #1021 → #1030
  → #1050 → #1057 → #1035 → #1040 → #1045 → #1039 → **#1017** (docs,
  hard-deps on #988).
- **routers/extensions.py** (8 PRs) — order: #1022 (foundation) → #1054
  → #1044 → #1056 → #1038 → #1045 → #1037.
- **setup-wizard** (4 PRs) — #1003 first, then drafts together
  (#1015 + #1018 + #1019).

## Cross-PR patterns worth a strategic decision

### A. Stack discipline for Yasin's sweep

63 of 75 open PRs are from Yasin. A "stack PR" convention (parent
branch + dependent children) would reduce his rebase toil by ~10× and
make merge order legible. Worth a one-time conversation: *"For 5+ PRs
against the same file, stack them with explicit parents — we'll merge
the train, not 14 individual rebases."*

### B. Resolve the BATS regression early

Q1 in [`research/questions.md`](../research/questions.md). Until the
1-line BATS fix lands, every PR's CI rollup is misleading. This is
amplifying review cost on every PR.

### C. The "no cloud" headline is unspecified at the recipe-vs-product line

PR #983 surfaces this. The README and marketing say "no cloud, no
subscriptions." A recipe under `resources/p2p-gpu/` for deploying onto
Vast.ai is, for the strict reader, a contradiction. For the relaxed
reader, recipes are recipes. **Either answer is fine — but the answer
needs to exist** so future "deploy on cloud GPU" or "deploy on serverless"
PRs have a clear line.

### D. Mobile (#961) is a roadmap question

Adding a fourth platform with two runtimes (Android Python + iOS WASM)
is a substantial commitment. The right answer might be "yes, but as a
companion repo we link to" — keeps the brand and gives the contributor
a path. Or "no, not now" with thanks. **Saying nothing is the worst
outcome** because the contributor's effort sits unrecognized.

## AMD-relevant changes (called out per the brief)

DreamServer's AMD developer-program partnership means AMD-touching PRs
get an extra eyeball. From the audit:

- **PR #750 (AMD Multi-GPU, y-coffee-dev)** — The flagship AMD PR.
  **Architecture sound, real-hardware tested, CI green, awaits maintainer
  re-review.** Cannot be auto-merged from this audit. Recommendation:
  cherry-pick the BATS fix (priority 1 above), then walk Y through your
  CHANGES_REQUESTED feedback, then merge after a confirm-on-real-hardware
  pass.
- **PR #1004** (Yasin, "skip compose.local.yaml on Apple Silicon to
  avoid llama-server deadlock") — Apple Silicon path; touches the
  resolver. Does NOT regress AMD; does NOT touch AMD code.
- **PR #1005, #1013, #1016, #1025, #1048, #1049** — Various Apple-
  silicon and macOS polishes. None touch AMD paths.
- **PR #1027** binds community extension ports via `${BIND_ADDRESS}` —
  applies to all platforms including AMD installs. Verify default
  remains loopback (per the LB policy in
  [`research/upstream-context.md`](../research/upstream-context.md) §6).
- **No PR in this audit** *regresses* AMD support. The risk is
  exclusively in #750 itself, where a wrong implementation could break
  multi-GPU AMD installs that don't currently exist on `main`.

## What this audit could NOT verify (be honest about it)

- **Real AMD multi-GPU hardware** — not on the auditor's box. PR #750's
  hardware-specific code paths were inspected, not exercised.
- **Apple Silicon paths** — auditor on Windows; macOS code was read,
  not run.
- **AMD Strix Halo / Lemonade** — neither present.
- **Mobile (Termux / a-Shell)** — PR #961's runtime cannot be tested
  without phone hardware.
- **Long-running install paths** in Docker containers — auditor did
  not run a full installer-in-Linux-container baseline-vs-PR comparison
  for every installer-touching PR; instead, the BATS fix unblocking 72
  PR signals was identified as the higher-leverage move.

When a verdict says "MERGE," it's based on diff inspection + CI signal
(filtered for the BATS regression) + cross-PR consistency check, not
end-to-end execution. The maintainer should run a final CI sweep on
the merge stack before each non-trivial merge.

## What's in this audit (one-line recap of each artifact)

- [`report/backlog-strategy.md`](backlog-strategy.md) — recommended merge
  sequence for clearing the backlog
- [`report/project-health.md`](project-health.md) — patterns the backlog
  reveals about the project
- [`report/contributor-notes.md`](contributor-notes.md) — per-contributor
  observations and feedback themes
- [`analysis/dependency-graph.md`](../analysis/dependency-graph.md) —
  cross-PR map (the second-highest-value file after this one)
- [`analysis/risk-matrix.md`](../analysis/risk-matrix.md) — per-PR scores
- [`analysis/surface-area.md`](../analysis/surface-area.md) — file-level
  fan-out
- [`prs/pr-{N}/verdict.md`](../prs/) — per-PR verdicts
- [`research/questions.md`](../research/questions.md) — questions that
  came up (read Q1 even if you read nothing else)
- [`testing/reproductions/repro-bats-docker-cmd-arr.sh`](../testing/reproductions/repro-bats-docker-cmd-arr.sh) — BATS bug repro
- [`decisions/0001-risk-scoring-methodology.md`](../decisions/0001-risk-scoring-methodology.md) — ADR for the risk-scoring
- [`tool-log.md`](../tool-log.md) — append-only audit-trail of consequential
  tool calls

Total file count: ~525 files across 75 PR directories + scaffolding.
