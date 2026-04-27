# PR #988 — Verdict

> **Title:** fix(security): bind llama-server and host agent to loopback
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/security-loopback`
> **Diff:** +47 / -17 across 8 file(s) · **Risk tier: Medium (score 10/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/988

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | 8 files across 3 OS targets (Linux scripts, macOS shell, Windows PS) + the host-agent Python and `.env.{example,schema.json}` |
| B — Test coverage | 2 | The bind-address logic isn't exercised by BATS or pytest in the repo; PR adds none |
| C — Reversibility | 1 | Pure code change; revert with `git revert` is clean. Existing installs with custom `BIND_ADDRESS` continue working. |
| D — Blast radius | 4 | Security-related: this *closes* a default-permissive binding. If wrong, a default install loses *containers can reach llama-server* — first-boot regression on Linux when bridge detection fails |
| E — Contributor | 0 | Yasin, established core; consistent with existing patterns |
| **Total** | **10** | **Medium** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE — first.** The single highest-priority merge in the queue.

The PR is a defensible cross-platform fix for a default-permissive bind that
the project's stated security policy (`research/upstream-context.md` §6:
"Every service binds to `127.0.0.1` by default") was supposed to apply to
already. SECURITY_AUDIT.md H3 found the same class of problem in OpenClaw
(PR #67 fixed OpenClaw); this PR finishes the job for `llama-server` and
the host agent.

Why merge first:

- **PR #1017 is hard-blocked on this PR.** Title literally says
  `docs(security): Linux host-agent fallback is 127.0.0.1 post-#988` —
  merging #1017 first ships docs claiming a behavior the code doesn't
  yet have.
- **Lowest-regression-risk security fix in the queue.** Default path
  (Docker Desktop on Mac/Win, working bridge detection on Linux) is
  unchanged. Only the *fallback when bridge detection fails on Linux*
  moves from `0.0.0.0` to `127.0.0.1`.
- **Architecturally clean** — uses the `BIND_ADDRESS` knob from PR #964
  (merged 2026-04-15), not a parallel knob. Threads it through every
  native-server launch site: macOS dream-macos.sh + install-macos.sh,
  Windows dream.ps1 + install-windows.ps1 (both Lemonade and llama.cpp
  in each), Linux bootstrap-upgrade.sh, and bin/dream-host-agent.py.

## Caveats — do these as a follow-up, not a block

- The `grep '^BIND_ADDRESS=' "$ENV_FILE" 2>/dev/null | cut … | tr … || echo ""`
  pattern in bash sites is identical to what already exists in
  `installers/phases/13-summary.sh:340`. It's a project-wide style
  violation per `CLAUDE.md` ("never `|| true` or `2>/dev/null`"), but
  **consistent with main** — this PR doesn't make it worse. A separate
  convention-fix PR should clean all call sites.
- No tests added. PR #1018 (draft, Yasin) is staking out adjacent BATS
  coverage; that's the right place for "bind defaults to loopback in
  every platform's launch path".
- The host-agent warning message change at `bin/dream-host-agent.py:2247-2252`
  is a substantive behavior change disguised as a comment-level diff.
  Worth one line in release notes: *"On Linux machines where Docker
  bridge detection fails, the host agent now binds to 127.0.0.1 (was
  0.0.0.0). Containers may not reach the agent in this rare case; set
  DREAM_AGENT_BIND= to override."*

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #1017 (draft) | **Hard dependency.** Title says "post-#988". Block #1017 until #988 lands. |
| #1027 | Soft alignment — both apply `BIND_ADDRESS` defaulting; #1027 does it for community extensions. Either order works. |
| #1044 | Soft alignment — #1044 teaches the dashboard scanner to *recognize* the `${BIND_ADDRESS:-127.0.0.1}` pattern. Merge #988 then #1044. |
| #1046 | **Tension to flag, not regression.** Title says `bind Next.js 16 to 0.0.0.0 inside container`. The 0.0.0.0 is the *container-internal* listen socket; host-side mapping stays loopback. Verified — see `prs/pr-1046/verdict.md`. |
| #1050 (FS preflight) | Different security class but same review wave. Merge after #988. |

## Trace

- Diff base SHA: see `raw/diff.base.sha`
- BIND_ADDRESS source-of-truth: `installers/phases/06-directories.sh:257`
- Existing same-pattern reader: `installers/phases/13-summary.sh:340`
- Security audit prior art: `SECURITY_AUDIT.md` §H3 (OpenClaw)
- PR #964 merge: 2026-04-15
- Hard dependency for: PR #1017
- See `prs/pr-988/review.md` and `prs/pr-988/diff-analysis.md` for the line-by-line read.
