# Project Health

What the open-PR backlog reveals about the DreamServer project. Less a
verdict on any individual PR; more a read of the pattern from the air.

## Headlines

1. **The project is in vigorous health.** 75 open PRs in two months on a
   400+-star OSS project means contributors care and the codebase is
   active. The default verdict for most PRs is MERGE; this is not a
   project where the backlog is full of dead-ends or code that doesn't
   work.

2. **63 of 75 PRs are from one contributor (Yasin).** That is **84%**.
   This is the project's biggest single risk: the bus factor on
   contributor breadth. It's also a sign of trust — Yasin is doing what
   most projects' core team does for free.

3. **The CI signal has been broken at HEAD since at least 2026-04-23.**
   72 of 75 PRs failing the same BATS assertion is a single
   one-line bug on `main`. That this hasn't been fixed in five days
   suggests either nobody noticed (likely — green-on-green-on-green-on-
   red is easy to dismiss as "this PR is broken") or noticed and didn't
   prioritize (possible — release-cadence is high).

4. **Convention adherence is strong.** Across the diffs reviewed in
   depth, the project's `CLAUDE.md` rules ("no broad catches, no
   fallback chains, no `2>/dev/null`, lib/phases purity") hold. Where
   they don't hold, the violations are **inherited from existing main**
   — i.e., the convention drift predates the open PRs.

5. **AMD partnership is well-served.** The flagship AMD PR (#750) is
   architecturally sound, real-hardware tested, and has thorough test
   coverage. AMD-touching code in other PRs uses `${BIND_ADDRESS}` and
   `compose.amd.yaml` patterns consistently. **No PR in this audit
   regresses AMD support.**

## What's working well

### Conventional Commits + focused PR scope (most PRs)

PR titles follow the project's `type(scope): subject` convention almost
universally. Typical examples from the open queue:

- `fix(host-agent): runtime hygiene — narrow pull, surface failures, normalize bind volumes`
- `fix(installer): block non-POSIX INSTALL_DIR + verify Docker Desktop sharing`
- `feat(dream-cli): --json flag on list/status and document doctor --json`

This is rare in 75-PR backlogs. It cuts the cognitive cost of triage
roughly in half. Yasin in particular writes PR bodies that explain
*why* and not just *what*; a few of his bodies (#988, #1003, #1050)
include explicit testing notes.

### Defensive tests across the stack

- Shell: BATS unit tests, contract tests, smoke tests
- Python: pytest with mocking + coverage
- Compose: validate-compose workflow validates layered files
- Cross-platform CI: matrix-smoke runs 6 distros (Ubuntu, Debian,
  Fedora, Arch, openSUSE)
- macos-smoke / powershell-lint cover the non-Linux paths
- Real-hardware fixture files (#750) for ROCm

This is heavier coverage than most OSS Bash-heavy projects manage.

### Architecture documentation is complete and accurate

The single most useful thing to a fresh auditor (the auditor!) was the
combination of `ARCHITECTURE.md`, `CLAUDE.md`, and `SECURITY_AUDIT.md`.
All three are accurate, current, and explicit about design choices and
tradeoffs. `CLAUDE.md`'s "Let It Crash > KISS > Pure Functions > SOLID"
priority order is the sort of thing that lets a reviewer evaluate a
diff without asking "is this how we do it?" for every line.

### The lib/phases purity boundary is a useful design invariant

`installers/lib/*.sh` files in the open PRs are pure. `installers/phases/*.sh`
files are imperative. New work respects this boundary; the AMD multi-GPU
PR's new lib (`amd-topo.sh`) is verifiably pure. The boundary works.

## Patterns worth attention

### Pattern 1: file convergence under one contributor

15 PRs touching `dream-cli`, 10 touching `dream-host-agent.py`, 8
touching `routers/extensions.py`, 6 touching `Extensions.jsx` — all from
Yasin, all submitted in parallel rather than as a stack.

This isn't dysfunctional. Yasin is moving faster than a stack-PR
workflow can keep up with. But it pushes the merge-conflict cost onto
the maintainer (in the form of conflict resolutions during merge) or
onto Yasin (in the form of 14 separate rebases).

The right shape: a brief "for 5+ PRs against the same file, can we
stack them?" conversation. The cost is one sit-down; the benefit is
maybe halving the maintainer's per-merge friction for the rest of the
year.

### Pattern 2: drafts left as drafts

15 of Yasin's PRs are in draft state. Several are exploratory companion
PRs to non-draft work (e.g., `test/dream-cli-bats-coverage` to the CLI
fixes). Drafts in the queue are signal noise — reviewers don't know
whether to engage.

A "draft = WIP, please review when ready" convention helps. Either
mark them ready or close them.

### Pattern 3: stale CONFLICTING PRs from non-core contributors

#351 (reo0603, input-validation tests) and #364 (championVisionAI,
dashboard-api APIs) are both from March, both CONFLICTING. They're the
shape of contributor goodwill that gets eroded if it sits unaddressed.

Both PRs have legitimate merit (real test additions, real endpoint
contracts). The right move is a brief, kind, deadlined message: "would
you rebase, here's the gap, two weeks, otherwise we'll close — happy
to revisit later." This costs nothing and leaves the contributor
relationship intact.

### Pattern 4: "while I'm here" scope creep absent

Reading the diffs in depth (the 9 high-priority verdicts, plus spot-
checking ~10 others), the auditor did **not** find a single instance
of "while I'm fixing X, also Y in a different file" sneak-in. PR
scopes match titles. This is rare and worth recognizing.

### Pattern 5: cross-platform discipline is paying off

PRs that touch one OS (#988, #1050) deliberately update all three
installer entry points (Linux scripts, macOS shell, Windows PowerShell)
in the same PR. This means the platform-divergence cost is being paid
*at write time* rather than accumulating. macOS-specific PRs (#1004,
#1005, etc.) explicitly state they don't regress Linux.

## Patterns worth flagging

### Flag 1: the BATS regression is a leading indicator

A 1-line bug on `main` poisoning all 72 PR CI signals for ~5 days
without a fix is a meta-signal about something: review attention is
elsewhere, or red CI is being normalized. Either is worth noticing.

When red CI is normalized, real CI signals get lost in noise. The fix
is fast, but the *pattern* of "this sat for 5 days" is the thing to
notice.

### Flag 2: dependabot bumps are not a healthy backlog item

Two dependabot PRs (#990, #991) for action version bumps. These should
auto-merge; they're failing CI on the BATS regression but otherwise
green. The fact they've been open for ~4 days suggests dependabot is
firing into a queue where it's not getting auto-attention.

A rule: dependabot for `.github/workflows/` actions = auto-merge after
CI green. The cost-benefit is overwhelmingly in favor.

### Flag 3: the bounty system's signal isn't visible in PR metadata

The brief mentions a bounty tier ($40 / $150 / $400). PR metadata
doesn't carry a tier label. Inferring tier from scope is doable
(see `report/contributor-notes.md`) but adds review cost — and means
disputes about "this looked Small but is Medium" can't be resolved
mechanically.

A label convention (`bounty/small`, `bounty/medium`, `bounty/large`)
on each bounty-claimed PR would surface this. Costs nothing to add at
intake.

### Flag 4: no PR in the queue addresses SECURITY_AUDIT.md C1, H1, H2 findings

`SECURITY_AUDIT.md` (latentcollapse, 2026-03-08) found:

- **C1** committed LiveKit credentials in `resources/frameworks/voice-agent/`
- **H1** static SearXNG `secret_key` shipped with every install
- **H2** `eval $env_out` pattern in `installers/lib/detection.sh:32`

The open PRs address H3 (PR #67 closed for openclaw, PR #988 in this
audit for llama-server / host-agent), but **C1, H1, H2 are not
represented** in the open PR queue. Either the maintainer is handling
these out-of-band (most likely for C1 — credential rotation) or they're
on the backlog.

Worth confirming the trio is tracked somewhere — open issues, security
advisory, separate workstream. They're not in the PR queue.

## Long-term observations

### The project's contributor model is unusual

Bounty + AMD partnership + 400+ stars + a single core contributor
moving at speed. Most OSS projects with this much activity have either
(a) a corporate backer with a paid team, (b) a volunteer team of 5-10
core, or (c) a much slower release cadence. DreamServer has none of
those — Michael + Yasin (and bursty contributions from others) is
holding the cadence, with the bounty system bringing in surge work.

The audit's read: this works **as long as Yasin doesn't burn out**.
Stack-PR discipline (Pattern 1) and acknowledging the bounty PRs
(Pattern 3) are the levers that reduce his per-PR cost.

### The "no cloud" branding intersects the contributor pipeline

PR #983 (Vast.ai p2p-gpu) is a thoughtful contribution that violates
the brand's headline. The bounty system likely pulls some contributors
who haven't internalized the "no cloud" stance — they see "deploy
DreamServer" and think "where can I deploy DreamServer." That's not a
bad thing — it's free pull-through reach to cloud-curious users — but
it does require a documented stance to keep future "deploy on X" PRs
clear.

A short FAQ entry — *"Why is DreamServer 'local-only' if there's a
Vast.ai recipe in resources/?"* — would close the loop.

### The lib/phases architecture is the right call for the codebase

The single biggest reason this audit produced clear verdicts at scale
is the project's separation of concerns. Pure libs, imperative phases,
schema-driven extensions, manifest-validated services. Reviewing a PR
that touches `installers/lib/` is *constrained* by the boundary; you
know what kinds of changes are valid. Reviewing a PR that touches
`installers/phases/10-amd-tuning.sh` is *constrained* differently;
you know it's allowed to touch sysctl and GRUB but should still be
guarded.

This architecture is paying back every review session. It would not
have been an obvious choice for a Bash-heavy installer project five
years ago. It's worth keeping pristine.

## Two-sentence summary

The DreamServer project is in vigorous health with one quirk: 84% of
open PRs are from a single contributor doing a methodical sweep, which
needs a 5-minute "let's stack these" conversation before the merge
queue scales further. The CI is suffering from a single broken BATS
test on `main` that should be fixed today; once that's in, the whole
backlog looks roughly half as scary as it does right now.
