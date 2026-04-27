# Backlog Strategy

## Recommended Merge Order

### Phase 1 - Foundation / Low-Regret Utilities

Merge:

`#1006, #1007, #1008, #1023, #1014, #993, #992, #991, #990`

Why: these are low-risk helper, test, dependency, and output-contract fixes. They reduce noise and unblock stricter Bash/CI work.

### Phase 2 - Security And Platform Defaults

Merge:

`#988, #1050, #1048, #1005, #1013, #996, #1026`

Why: these harden install and runtime defaults across macOS/Windows/Linux. Merge #988 before docs that describe host-agent/native binding.

### Phase 3 - Extension Runtime Contracts

Merge:

`#1021, #1044, #1035, #1036, #1034, #1028, #1049, #1047, #1046`

Why: #1021 and #1044 are prerequisites for several blocked PRs. The rest are compose/library fixes that validate cleanly.

### Phase 4 - Dashboard / API / Setup

Merge:

`#1025, #1022, #1010, #1009, #1003`

Why: targeted tests passed and each change is bounded to a clear dashboard/API behavior.

### Phase 5 - Resolver / Apple / Docs

Merge:

`#1004, #999, #997, #959`

Why: these are safe after the earlier foundations land. #959 is documentation-only and reduces Token Spy confusion.

## Revise Before Merge

Highest-value revise requests:

- **#750:** pass `--gpu-count "${GPU_COUNT:-1}"` through every resolver refresh/cache caller; rerun AMD multi-GPU tests.
- **#1032:** stack on #1021 or include the host-agent `--no-deps` removal.
- **#1027:** stack on #1044 or include the scanner parser update.
- **#1054:** enforce deployable compose on direct server install path.
- **#1056:** harden malformed `deploy.resources` scanner shape.
- **#1057:** make pull filtering dependency-aware.
- **#1043:** include embeddings in RAG opt-out.
- **#1000:** keep JSON stdout clean when registry warnings occur.

## Reject / Close

- **#966:** close as superseded/redundant. Current diff adds no useful mergeable delta.

## Queue Hot Spots

1. **Strict Bash / pipefail cluster:** #1006, #1007, #1008, #1018, #1002, #998, #1016, #1011.
2. **Extension install lifecycle cluster:** #1021, #1032, #1030, #1039, #1040, #1057, #1054, #1045.
3. **Bind-address/security scanner cluster:** #988, #1044, #1027, #973, #1017.
4. **Docs consistency cluster:** #973, #966, #959, #1055, #1017.
5. **GPU/AMD cluster:** #750, #1009, #999, #1025, #1020, #983.

The backlog gets substantially safer if these clusters are handled as chains, not individual PRs.
