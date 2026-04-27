# Executive Summary

## Headline

I audited all 75 open DreamServer PRs. Final recommendation:

| Recommendation | Count |
|---|---:|
| Merge | 34 |
| Revise | 40 |
| Reject | 1 |
| Total | 75 |

The queue is mergeable, but not by simple age or green-check sorting. The high-value path is to merge the focused, well-tested foundation PRs first, then ask for small targeted revisions on the PRs that are directionally right but currently break install, extension, security, or AMD paths.

## Three Highest-Priority Merges

1. **#1021 - remove `--no-deps` from extension install start path.** This enables real compose `depends_on` semantics for extension sidecars and cross-extension dependencies. Several later PRs only become correct after this lands.
2. **#1044 - scanner accepts `${BIND_ADDRESS:-127.0.0.1}` safely.** This unlocks the extension bind-address sweep and keeps the no-LAN-by-default security contract.
3. **#988 - bind native/host-agent fallbacks to loopback by default.** This is the most important default-security improvement in the queue and should land before broad doc updates that describe binding behavior.

## Three Highest-Risk Situations

1. **Installer/host-agent churn is fragmented.** Many PRs independently touch install phases, host-agent lifecycle, compose flag resolution, and strict-mode Bash behavior. Merge focused fixes first (#1006, #1007, #1008, #1021, #1023, #1044, #988), then rebase broad drafts.
2. **AMD multi-GPU support is strategically important but not merge-ready.** #750 is the AMD developer-program flagship PR in the queue. It has good architecture and passing dashboard AMD tests, but resolver refresh call sites can drop `docker-compose.multigpu-amd.yml` unless they pass `--gpu-count`. Do not merge it until that is fixed and rerun on real AMD hardware or documented simulation.
3. **Dashboard extension install security is improving but incomplete.** #1054/#1056/#1057/#1045 move in the right direction, but each has a missing server-side edge case. These should be revised as a small security-hardening bundle rather than merged piecemeal.

## AMD-Relevant Callouts

AMD support is a project-level reputational surface because of the AMD developer program partnership. Treat these with higher scrutiny:

- **#750 revise:** flagship AMD multi-GPU support. Needs compose resolver call-site fix and hardware validation record.
- **#1009 merge:** image generation defaults now match backend capability, including AMD/NVIDIA true and base/CPU/Apple false.
- **#1025 merge:** Apple-specific dashboard GPU detail, not AMD, but important to avoid cross-platform GPU regressions.
- **#999 merge:** Apple CLI/doctor handling; keeps non-NVIDIA GPU paths from being treated as broken NVIDIA.
- **#1050 merge:** platform filesystem hardening reduces install-support load across macOS/Linux/Windows.
- **#983 revise:** NVIDIA/P2P GPU repair logic is not AMD, but it is GPU-infrastructure code and should not land broken.

## Merge-Now Set

Merge candidates, subject to CI and the order in `backlog-strategy.md`:

`#1050, #1049, #1048, #1047, #1046, #1044, #1036, #1035, #1034, #1028, #1026, #1025, #1023, #1022, #1021, #1014, #1013, #1010, #1009, #1008, #1007, #1006, #1005, #1004, #1003, #999, #997, #996, #993, #992, #991, #990, #988, #959`.

## Revise / Reject Summary

The 40 revise PRs are not all bad. Most are useful but blocked by one of four patterns:

- They need a small correctness fix (#1056, #1054, #1043, #1033, #1024, #1018, #1000, #994, #750).
- They need prerequisite merge order or rebase (#1032, #1027, #1040, #1039, #1017, #1016).
- They are drafts or stacked on closed/unmerged bases (#1037, #1038, #1011, #1015, #1020).
- They touch high-risk security/automation paths and need architecture hardening (#961, #983, #1045, #1057).

Only one PR is a clear reject:

- **#966 reject for redundancy.** Its current diff from the merge base is empty or already absorbed by later docs work.

## Strategic Maintainer Decision

Before clearing the queue, decide that DreamServer will prioritize:

1. Secure defaults over convenience in host-agent/native service binding.
2. Compose resolver correctness as a shared contract, not an incidental helper.
3. AMD multi-GPU support as a flagship feature that requires hardware-backed validation before merge.
4. Smaller focused PRs over broad drafts that combine strict-mode, UX, docs, and installer behavior.

That decision turns the backlog from 75 independent debates into a manageable sequence of merge foundations, revise requests, and closes.
