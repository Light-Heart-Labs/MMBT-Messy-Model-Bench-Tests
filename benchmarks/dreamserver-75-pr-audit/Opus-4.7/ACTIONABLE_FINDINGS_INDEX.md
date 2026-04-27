# Actionable Findings Index

The line-level issues this audit surfaced that the maintainer can act on
immediately. Sorted by leverage (highest impact / lowest cost first). Each
entry points to the per-PR verdict for full reasoning.

## Highest leverage

### F1 — The BATS regression on `main` is poisoning 72 of 75 PR CI signals

`dream-server/tests/bats-tests/docker-phase.bats:100`:
```diff
-    assert_output $'sudo\ndocker'
+    assert_output "sudo docker"
```

`echo "sudo" "docker"` outputs `sudo docker` (one line, space-separated).
The assertion `$'sudo\ndocker'` expects two lines. Test has been wrong on
every bash version. PR #750 bundles the fix as one of 33 files; cherry-pick
that one line to its own trivial PR.

**Cost:** ~5 minutes. **Impact:** 72 PR CI signals become trustworthy.
**Reproduction:** `testing/reproductions/repro-bats-docker-cmd-arr.sh`.
**Verdict:** see `prs/pr-750/verdict.md` and `research/questions.md` Q1.

### F2 — Default-permissive bind on llama-server and host agent (PR #988)

`bin/dream-host-agent.py:1944` and `:2241` plus all native llama-server
launch sites. PR #988 is the cross-platform fix. Hard dependency for #1017
(literally titled "post-#988") and for #973's SECURITY.md additions.

**Verdict:** `prs/pr-988/verdict.md` (MERGE — first).

### F3 — `chmod 600` on FAT/exFAT/NTFS is a silent no-op (PR #1050)

`.env` carries `DASHBOARD_API_KEY`, `LITELLM_KEY`, provider API keys.
Installing on FAT/exFAT/NTFS leaves them world-readable. PR #1050 blocks
non-POSIX `INSTALL_DIR` at install time + defense-in-depth at runtime via
host-agent `_fs_type()`.

**Verdict:** `prs/pr-1050/verdict.md` (MERGE — second-priority security).

## High leverage

### F4 — PR #1037 + #1038 share ~100 lines of identical "unhealthy status" code

Both add the same `unhealthy` extension status (backend bucket + UI badge +
filter chip + "Check Logs" button). Per `analysis/dependency-graph.md`,
**merge #1038 first** so #1037 becomes a UI-only delta. Otherwise the
maintainer resolves a 100+ line conflict twice.

### F5 — PR #1030 has a likely test bug (`tests/test_host_agent.py:236`)

Asserts the literal substring `"did not reach running state within 15s"`
against `inspect.getsource(_handle_install)`. Production code uses an
f-string (`f"...within {startup_timeout}s..."`) — the source contains
`{startup_timeout}s`, not `15s`. PR claims 44/44 passing; this assertion
is suspicious. **Verify before merge.** Verdict: REVISE — small.

### F6 — PR #1026 introduces SIX new `2>/dev/null` redirects

In newly-added bash blocks at Linux Phase 13 + macOS Phase 6. Convention
violation per `CLAUDE.md`. **Easy fix:** drop them, let stderr surface to
the existing `ai_warn` else-branch. Verdict: REVISE — small.

### F7 — PR #1039 + #1040 + #1045 carry duplicate `_find_ext_dir` + bind-mount filter widening + 15s state poll

Triple-overlap in `bin/dream-host-agent.py`. Whichever lands first forces
rebase on the other two. **Pick a primary.** PR #1057 takes a different
angle on the same `_precreate_data_dirs` function (dict-form support).

### F8 — PR #1040 bundles unrelated install-flow churn

The langfuse-only delta (post_install.sh hook + manifest registration +
reproducer) is good. But it bundles ~92 lines of unrelated install-flow
churn duplicated across #1039 + #1045. **Strip from this one;** one PR
should own that change. Verdict: REVISE — small.

## Medium leverage

### F9 — PR #351 has a committed git conflict marker (REJECT)

`dream-server/extensions/services/dashboard-api/tests/test_routers.py:111`:
```
>>>>>>> 8a44877 (test: add comprehensive...)
```
File is unparseable Python on merge. **Close politely** or have reo0603
extract the test additions onto a fresh branch.

### F10 — PR #990 (dependabot github-script v8 → v9) is a documented breaking change

`@actions/github` becomes ESM-only; `require('@actions/github')` no longer
works inside `script: |` blocks. **Manual grep required** before merge:
- `.github/workflows/autonomous-code-scanner.yml:1225,1260`
- `.github/workflows/claude-review.yml:222,424,463`

Verdict: HOLD — needs maintainer judgment.

### F11 — PR #973 should land *after* #988

PR #973 adds a `SECURITY.md:79-103` "Host Agent Network Binding" section
documenting post-#988 behavior. Same gating principle as PR #1017. Don't
merge #973 first or the docs claim a behavior the code doesn't yet have.

### F12 — PR #997 removes a `docker exec ... /bin/bash || /bin/sh` retry chain

Pre-existing `CLAUDE.md` violation in main. PR #997 replaces with explicit
branching. **Direction-of-change positive signal.**

### F13 — PR #1027 ships a static enforcement gate for BIND_ADDRESS loopback

`tests/test-bind-address-sweep.sh` enforces the loopback default policy
across all 29 community extensions. **Strengthens the security policy from
#988** with a regression-shield. Worth surfacing — it's a defense-in-depth
contribution disguised as a 31-file change.

### F14 — PR #998 + #1002 share 6+ identical hunks

Both branches share a base. Merge order is mechanical: **#1008 → #998 →
#1002**. #1002 will rebase clean once #998 lands.

## Lower leverage but worth noting

### F15 — PR #716 weakens production defaults to fix a CI symptom

Targets `resources/dev`, not `main`. The validator-side change is correct;
the compose-side change (`FRIGATE_RTSP_PASSWORD:?must be set` →
`FRIGATE_RTSP_PASSWORD:-frigate`) should be reverted. Verdict: REVISE —
small.

### F16 — PR #1046 confirmed not a #988 regression

Title looked alarming (`bind Next.js 16 to 0.0.0.0 inside container`) but
the 0.0.0.0 is the *container-internal* listen socket; host-side mapping
`${BIND_ADDRESS:-127.0.0.1}:...:3000` was untouched. **Merge OK.**

### F17 — PR #1047 leaves `NEXTAUTH_URL` correctly untouched

While sweeping in-container healthcheck URLs to `127.0.0.1`, the OAuth
callback URL is browser-evaluated and must stay as the hostname users see.
Author got this right.

### F18 — PR #1056 multi-concern is genuinely tied together

Catalog timeout + orphaned whitelist + GPU passthrough scan + health_port
— all four are real user-extension path bugs, not scope creep. Title sounds
broad; diff is focused.

## Strategic findings (not line-level, but actionable)

### S1 — Stack-PR convention for Yasin's sweeps

63 of 75 open PRs are by Yasin. 14 PRs touch the 45K-line `dream-cli` Bash
file. Merging individually = 13 conflict-resolutions, all his to redo. A
brief "for 5+ PRs against the same file, can we stack them?" conversation
saves Yasin (and the maintainer) substantial repeated work. See
`report/contributor-notes.md`.

### S2 — Three strategic HOLDs need maintainer judgment

- **#364** (stale dashboard-api APIs, March): reach out + deadline + close.
- **#961** (mobile Termux + iOS, 6,891 lines, first PR): roadmap question.
- **#983** (Vast.ai p2p-gpu): "no cloud" positioning question.

Each verdict.md proposes A/B/C paths and what a kind contributor message
looks like.

### S3 — SECURITY_AUDIT.md C1 + H1 + H2 are not represented in the open PR queue

C1 (committed LiveKit credentials), H1 (static SearXNG `secret_key`), H2
(`eval $env_out` in detection.sh) are all unaddressed in open PRs. Either
out-of-band workstreams exist or these are on the backlog. **Confirm
they're tracked somewhere.** Per `report/project-health.md` Flag 4.

---

For full reasoning on any item, open the corresponding `prs/pr-{N}/verdict.md`
or the noted report/research file.
