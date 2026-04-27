# Questions Log

## Q1: Is the extensions library meant to be part of the main repo?
**Context:** PRs #351, #364, #716 each add 150k+ lines to `resources/dev/extensions-library/`.
**Resolution:** Yes — the extensions library is part of the main repo. The `resources/dev/` path suggests it's a development/staging area, but the resolver scans it for available extensions. The library is meant to be curated, not pruned, but the PR size suggests it needs better management.

## Q2: Does PR #1037 duplicate PR #1045?
**Context:** Both PRs add "unhealthy" status handling to the extensions router.
**Resolution:** Yes — PR #1045 includes all of #1037's changes plus additional config sync logic. #1037 is superseded.

## Q3: Are PRs #991 and #990 superseded by #983?
**Context:** All three PRs bump CI action versions.
**Resolution:** Yes — PR #983 includes the same claude-code-action and github-script bumps plus additional Vast.ai toolkit work. #991 and #990 are superseded.

## Q4: Is the mobile support PR (#961) in scope?
**Context:** PR #961 adds Android Termux and iOS a-Shell support.
**Resolution:** No — the project's GPU-dependent architecture (llama-server, ComfyUI, etc.) requires desktop/server hardware. Mobile support would be a fundamentally different product. Rejected for fit.

## Q5: What's the relationship between PRs #351 and #364?
**Context:** Both PRs touch 864 files with ~158k lines each.
**Resolution:** They are near-duplicates — both add extensions library services, tests, and documentation. PR #364 has broader scope (dashboard API settings, voice runtime, diagnostics) and is the more comprehensive implementation. #351 is superseded.

## Q6: Does PR #750 (AMD Multi-GPU) conflict with any other PR?
**Context:** PR #750 adds AMD multi-GPU support.
**Resolution:** No direct conflicts. PR #1032 (depends_on mirror for continue) adds an AMD overlay that is compatible with #750. Both can be merged independently.

## Q7: What's the merge order for the host-agent PRs?
**Context:** 7 PRs modify `dream-host-agent.py`.
**Resolution:** #988 → #1030 → #1050 → #1057 → #1039 → #1038 → #1035. Each builds on the previous.

## Q8: What's the merge order for the CLI PRs?
**Context:** 12 PRs modify `dream-cli`.
**Resolution:** #998 → #1002 → #1008 → #1006 → #1007 → #994 → #993 → #999 → #1000 → #997 → #1016 → #1011. Each enables stricter bash modes or depends on previous changes.

## Q9: Is the bounty system working as intended?
**Context:** Three first-time contributors submitted 150k+ line PRs.
**Resolution:** The bounty system may be encouraging overly ambitious first contributions. A "Tiny" tier for first-time contributors (max 1,000 lines) would help.

## Q10: Does PR #988 (loopback binding) affect AMD compatibility?
**Context:** PR #988 changes the default bind address from 0.0.0.0 to 127.0.0.1.
**Resolution:** No — the loopback binding applies uniformly across all GPU backends. AMD ROCm containers are not affected.
