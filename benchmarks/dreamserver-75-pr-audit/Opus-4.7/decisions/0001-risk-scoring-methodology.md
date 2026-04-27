# ADR 0001 — Risk Scoring Methodology

**Status:** Accepted (auditor's choice)
**Date:** 2026-04-27
**Author:** Audit (Claude Opus 4.7)

## Context

Every PR needs a risk score so the maintainer can prioritize merges. With 75
PRs, a one-line gut score won't work — we need a methodology that's
reproducible, auditable, and explicit about what factors matter. The
methodology has to fit a project where:

- Most contributors are bounty-incentivized (varied trust priors)
- The codebase is multi-platform (Linux/Windows/macOS) and multi-GPU
- Some files are touched by 10+ PRs simultaneously
- CI is red across 72 of 75 PRs for a single pre-existing reason (see
  `research/questions.md` Q1)

## Decision

Each PR is scored on **five axes**, each `0` (lowest risk) to `4`
(highest risk). Total risk = sum (max 20). The score is composed of:

### Axis A — Surface area (0–4)

How many subsystems and files the PR touches.

| Score | Criterion |
|-------|-----------|
| 0 | 1 file, ≤10 lines |
| 1 | 1–3 files in one subsystem, <100 lines |
| 2 | 4–10 files, one subsystem, or 1 file >100 lines |
| 3 | Multi-subsystem, 100–500 lines |
| 4 | Cross-platform, >500 lines, or touches a hot-spot file (15+ PR overlap) |

### Axis B — Test coverage of affected code (0–4)

Inverse of confidence. Tests that exist + the PR runs them = low risk.

| Score | Criterion |
|-------|-----------|
| 0 | Affected code path has BATS, contract, or pytest coverage **and the PR passes those tests** (CI green for non-`integration-smoke` jobs) |
| 1 | Affected path has tests, but PR adds new logic the tests don't reach |
| 2 | Affected path has tests but they're inspection-only (no actual run) |
| 3 | Affected path has *no* tests; PR adds none |
| 4 | Affected path has no tests AND the PR adds non-trivial behavior change |

### Axis C — Reversibility (0–4)

How hard is it to back this PR out if it goes wrong?

| Score | Criterion |
|-------|-----------|
| 0 | Pure code change, no schema/storage migration; revert is `git revert` |
| 1 | Schema/config change with backwards-compatible defaults |
| 2 | Schema/config change requiring documented migration |
| 3 | Touches OS-level state (sysctl, modprobe, udev, GRUB) — phase 10 work |
| 4 | Modifies persistent on-disk state (DB schema, file layout) without migration script |

### Axis D — Blast radius if wrong (0–4)

If this PR ships and is wrong, who notices and how badly?

| Score | Criterion |
|-------|-----------|
| 0 | Internal-only (test, docs, CI tooling) — only contributors see breakage |
| 1 | Single optional service breaks; user can disable extension |
| 2 | Default service degraded; user notices but can work around |
| 3 | Install or first-boot fails on at least one platform |
| 4 | Security regression (binding to public, removing auth, leaking creds) OR install fails everywhere |

### Axis E — Contributor track record (0–4)

Trust priors based on prior merges and the PR's coherence.

| Score | Criterion |
|-------|-----------|
| 0 | Established core contributor with multiple merged PRs in this subsystem; PR shows familiarity (correct conventions, idiomatic) |
| 1 | Established contributor branching into a new subsystem |
| 2 | Bounty contributor with prior merged PRs that needed only minor revision |
| 3 | First-PR or near-first-PR contributor; PR is in scope but conventions drift |
| 4 | First PR + crosses architectural boundary OR PR shows pattern-mismatch (broad catches, fallback chains, etc.) |

Note: "Trust" is not a personal judgment. It's the auditor's confidence that
the PR matches the project's documented conventions (`CLAUDE.md`).

## Total → recommendation tier

| Total | Tier | Default action |
|-------|------|----------------|
| 0–3 | Trivial | Auto-merge candidate. Verdict file is short; no test run beyond inspection. |
| 4–8 | Low | Merge after surface-level review. Run tests if they exist. |
| 9–13 | Medium | Full review. Tests required (run if they exist; flag REVISE—missing-tests if they don't). |
| 14–17 | High | Full review + cross-PR check + at least one test environment exercise. Often gets HOLD or REVISE—architectural. |
| 18–20 | Critical | Maintainer judgment required. Often HOLD or REJECT—fit. |

## Why these axes

**Surface area** is the most-cited risk factor in PR review literature (cf.
Bird et al., Microsoft Research, 2011). Larger diffs hide more bugs.

**Test coverage** is second because uncovered code is uncovered behavior
change — the most common source of regressions in our setting.

**Reversibility** matters because the cost of a bad merge is bounded by how
fast you can roll back. Phase-10 AMD tuning (sysctl, modprobe) is a much
worse roll-back than a Python router fix.

**Blast radius** is the impact axis. A 4-line PR can be Critical if it removes
auth from a port-forwarded service.

**Contributor track record** is included reluctantly. The bounty model means
some PRs come from contributors who haven't internalized DreamServer's
"Let It Crash > KISS" philosophy and may add `try: except: pass` for the
"polish" of catching errors. We score these higher because the conventions
mismatch is a real risk vector, but we explicitly score *the PR's
adherence*, not the person.

## What this methodology deliberately does NOT score

- **PR age.** Older isn't worse. Stale PRs (#351, #364) are scored on their
  *current* state; if they need rebase, that's surfaced via `mergeable: false`,
  not via age.
- **PR size.** Already captured under surface area. Big-but-coherent
  (e.g. PR #750 AMD multi-GPU at 5,054 additions) and big-but-incoherent
  (sprawl) are different; the auditor's reading of `diff.patch` distinguishes.
- **CI status as a primary signal.** Because of Q1 (BATS regression), CI
  red is currently a noisy signal. Verdicts cite specific CI checks (e.g.
  `Lint Python`, `dashboard build`), not the rollup status.

## When the methodology breaks

If a PR scores **High** (14–17) on this rubric but the auditor reads the diff
and is confident it's safe, the verdict explains why the score overstates
risk. Conversely, a Low-score PR can still be REVISE/REJECT if review uncovers
something the rubric didn't anticipate — the rubric is a default, not a
mandate.

## How this informs verdicts

Each `prs/pr-{N}/verdict.md` file leads with:

```
| Axis | Score | Why |
|------|-------|-----|
| Surface area | 1 | Single file, 47 lines |
| Test coverage | 2 | BATS exists for affected path but PR adds logic outside it |
| Reversibility | 0 | Pure code, no schema |
| Blast radius | 1 | Optional voice extension |
| Contributor | 0 | Yasin, established in dream-cli |
| **Total** | **4** | **Low** |
```

Then the verdict prose. The score and the verdict are explicit about each
other.
