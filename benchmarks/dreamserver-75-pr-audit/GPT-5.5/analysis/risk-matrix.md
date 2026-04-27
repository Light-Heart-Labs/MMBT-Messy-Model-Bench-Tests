# Risk Matrix

## Methodology

Risk is scored from 1 to 10 using explicit axes:

| Axis | Signal |
|---|---|
| Surface area touched | Installer, host-agent, resolver, dashboard API, GPU, mobile automation, docs-only |
| Test coverage | Targeted tests passed, static proof only, no runnable proof, failing tests |
| Reversibility | Docs/test-only low risk; installer/security/GPU high blast radius |
| Blast radius if wrong | One feature path vs install/startup/security/AMD support |
| Contributor track record | Frequent contributor in same subsystem vs first/infrequent contributor |
| Cross-PR coupling | Independent vs depends/conflicts/supersedes |

The generated per-PR `verdict.md` files include a numeric risk score and reasons. The score is not a black box: it starts with base 2, adds for core/runtime surface, line-level findings, merge conflicts, and AMD relevance, and subtracts for tested/approved merge paths.

## Recommendation Counts

| Recommendation | Count |
|---|---:|
| Merge | 34 |
| Revise | 40 |
| Reject | 1 |

## Highest-Risk PRs

- #750 - AMD multi-GPU. High strategic value, high blast radius, currently revise.
- #961 - mobile local automation bridge. Security-sensitive local action endpoints, revise.
- #983 - P2P GPU repair. GPU infrastructure with unreachable repair branch, revise.
- #1057 - host-agent install pull filtering. Good intent but dependency-blind, revise.
- #1054/#1056 - extension install scanner hardening. Security-sensitive, revise.
- #351/#364 - old conflicting dashboard API/test PRs. Rebase/conflict risk.

## Low-Risk Merge Candidates

Docs/dependency/test polish with good proof: #1048, #1036, #1014, #993, #992, #991, #990, #959.

Low-risk code fixes with targeted proof: #1006, #1007, #1008, #1021, #1022, #1023, #1025, #1044.

## ADR Note

This matrix is also an ADR-style methodology decision: score disagreement should be resolved by changing the documented axes, not by changing unexplained numbers.
