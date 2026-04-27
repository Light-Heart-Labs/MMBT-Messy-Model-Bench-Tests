# PR #750 — Interactions

## Hard dependencies

**This PR has no hard dependencies on other open PRs.** It can land on the
current `main` directly (after addressing maintainer CHANGES_REQUESTED).

This PR is **not** a hard dependency for any other open PR — Yasin's
host-agent and dream-cli sweeps don't reference it.

## Soft conflicts (shared files with other open PRs)

| File | Other PRs touching | Notes |
|------|-------------------|-------|
| `dream-server/dream-cli` | #993 #994 #997 #998 #999 #1000 #1002 #1006 #1007 #1008 #1011 #1016 #1018 #1020 (Yasin's 14-PR cluster) | The biggest soft-conflict. #750 modifies `dream-cli` for AMD support; Yasin's PRs do mostly orthogonal cleanup. **Merge #750 *before* the Yasin cluster** so he rebases against it once, not 14 times. |
| `dream-server/.env.schema.json` | #988 #994 #1010 #1017 #1018 | Disjoint key sets. #750 adds AMD multi-GPU keys; others add unrelated keys. Trivial merge. |
| `dream-server/.env.example` | #973 #988 #992 #1013 #1017 | Same as schema — disjoint regions. |
| `dream-server/installers/phases/06-directories.sh` | (none in open set) | Clean. |
| `dream-server/installers/lib/detection.sh` | (none in open set) | Clean. |
| `dream-server/scripts/resolve-compose-stack.sh` | #1004 #1029 #1051 (resolver fixes) | #750 adds AMD-multi-GPU resolution path; #1004 / #1029 / #1051 fix unrelated resolver edge cases. Re-test resolver output after each merge. |
| `dream-server/extensions/services/dashboard-api/gpu.py` | #1025 (Apple Silicon GPU detection) | **Soft conflict that needs care.** #750 adds AMD branches; #1025 adds Apple branches. Both extend `gpu.py`; merge order is the concern but **no semantic conflict** — they extend different vendor branches. Merge in either order. |

## Supersession / collapse candidates

None. #750 is the canonical AMD multi-GPU implementation; no other open
PR overlaps its scope.

## The cherry-pick that should NOT happen alongside

**Don't merge #1004** (`fix(resolver): skip compose.local.yaml on Apple
Silicon`) at the same time as #750. Both touch
`scripts/resolve-compose-stack.sh`. Their changes don't textually conflict
but the resolver behavior on Apple is subtle. After whichever lands,
re-verify resolver output for AMD multi-GPU + Apple Silicon by exercising
the new validate-compose CI job that #750 adds.

## Recommendation for stacking with the BATS-fix cherry-pick

Per `verdict.md`, recommend: yank `tests/bats-tests/docker-phase.bats:100`
fix (1 line) to a separate trivial PR. Two reasons:

1. The BATS fix is independent of AMD multi-GPU. Bundling them means the
   72-PR CI unblock is gated on AMD review.
2. After the cherry-pick lands, every PR's CI signal becomes
   *interpretable* — including #750's own remaining feedback cycle.
