# Contributor Notes

## Yasin Bursali (`yasinBursali`)

Yasin authored the majority of the queue. Pattern: high productivity, many narrowly scoped PRs, good PR-body explanations, but also many changes touching the same installer/host-agent/dashboard-api seams. The best Yasin PRs are focused and test-backed (#1021, #1044, #1006, #1008, #1035). The weaker ones are broad drafts or miss an adjacent path (#1057, #1056, #1054, #1045, #1030, #1018, #1000).

Feedback theme: keep the excellent decomposition, but require each PR to prove both the direct route and the bypass route. For server-side install/security fixes, UI/catalog behavior is not enough.

## `y-coffee-dev` / Y

Owns the AMD multi-GPU work (#750) and a runtime/API follow-up (#1052). #750 is valuable and aligned with the AMD partnership, but it has flagship-feature expectations: hardware validation, resolver integration completeness, and careful merge ordering. Treat it as a Large bounty even if the metadata does not carry the tier label.

Feedback theme: the architecture is promising; the revision should be precise, not a rewrite. Fix resolver call sites, rerun tests, and attach real AMD hardware proof.

## Dmytro (`boffin-dmytro`)

Docs/support contributor. #959 is useful and mergeable. #966 should be closed because it is superseded/empty. #1042 needs a path-format fix for support bundle JSON output under Git Bash.

Feedback theme: good instincts on user-facing support consistency, but docs/support tooling should be tested in the shell environments users actually run.

## Dependabot

#990 and #991 are acceptable dependency pin bumps. They were checked for known breaking script patterns and workflow YAML parsing.

Feedback theme: merge after CI; keep dependency bumps isolated.

## First-Time / Infrequent Contributors

- #351 has a conflict marker and cannot be evaluated until rebased.
- #364 is an older conflicting runtime API feature and removes unrelated coverage.
- #716 has a good validation idea but weakens production secrets.
- #961 adds mobile automation surfaces without enough local request protection.

Feedback theme: the project should require extra scrutiny for first-PR changes in installer, auth, automation, or API router code. These can be valuable, but they need tight tests and architecture review.

## Bounty-Tier Observations

Fetched PR metadata did not consistently expose Small/Medium/Large bounty labels. The per-PR verdict files therefore record the detected tier when present and otherwise mark it as not found in metadata. Maintainer should cross-check with the bounty tracker before payout decisions.

The apparent mismatch cases are still visible:

- #750 behaves like Large-scope work regardless of label.
- Small-looking docs/CI PRs can still block users if they document stale security or installer behavior.
- "Test-only" PRs are not auto-mergeable if they are conflict-dirty or unparsable (#351).
