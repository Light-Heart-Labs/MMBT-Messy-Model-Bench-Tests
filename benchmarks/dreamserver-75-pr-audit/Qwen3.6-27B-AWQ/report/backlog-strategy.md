# Backlog Strategy: Recommended Merge Order

## Phase 1: Security & Foundation (PRs 1-10)

These PRs establish security baselines and fix foundational issues. They must be merged first because subsequent PRs depend on them.

| Order | PR | Title | Rationale |
|-------|-----|-------|-----------|
| 1 | #988 | Security: bind llama-server and host agent to loopback | Security hardening; prerequisite for all host-agent PRs |
| 2 | #1030 | Install flow — built-in hooks, bind-mount anchor | Foundation for install flow PRs |
| 3 | #1050 | Block non-POSIX INSTALL_DIR + Docker Desktop sharing | Filesystem detection; prerequisite for #1057 |
| 4 | #1057 | Runtime hygiene — narrow pull, surface failures | Most impactful host-agent fix |
| 5 | #1039 | Retry install failure through hook + progress | Depends on #1057 |
| 6 | #1038 | Honor pre_start return, surface post_start failure | Depends on #1039 |
| 7 | #1035 | Openclaw recreate on install | Depends on #1038 |
| 8 | #1045 | Route extension config sync through host agent | Supersedes #1037 |
| 9 | #1056 | Catalog timeout, orphaned whitelist, GPU scan | Dashboard API polish |
| 10 | #1044 | Accept ${VAR:-127.0.0.1} in compose port scan | Compose pattern fix |

## Phase 2: CLI Hardening (PRs 11-22)

The CLI chain must be merged in order because each PR enables stricter bash modes or depends on previous changes.

| Order | PR | Title | Rationale |
|-------|-----|-------|-----------|
| 11 | #998 | pipefail + surface LLM failures + exit codes | Enables pipefail; prerequisite for all CLI PRs |
| 12 | #1002 | Enable set -u + guards for conditional variables | Enables set -u; depends on #998 |
| 13 | #1008 | Guard .env grep pipelines against pipefail | Depends on #998 (pipefail) |
| 14 | #1006 | Route log() and warn() to stderr | Clean command capture |
| 15 | #1007 | Double-quote tmpdir in gpu_reassign RETURN trap | Shell safety |
| 16 | #994 | Schema-driven secret masking + macOS Bash 4 | Credential security |
| 17 | #993 | Color-escape + table-separator + NO_COLOR | Visual polish |
| 18 | #999 | Apple Silicon coverage for gpu subcommands | Platform support |
| 19 | #1000 | --json flag on list/status | Feature addition |
| 20 | #997 | Pre-validate 'dream shell' service + Docker preflight | UX improvement |
| 21 | #1016 | Apple GPU output polish + SIGINT handling | Platform polish |
| 22 | #1011 | Bash 3.2 declare -A guard + validate routing | Compatibility |

## Phase 3: Small Fixes & Tests (PRs 23-45)

These are independent, low-risk PRs that can be merged in any order within this phase.

| Order | PR | Title | Rationale |
|-------|-----|-------|-----------|
| 23 | #1010 | Mark provider API keys as secret in schema | Security |
| 24 | #1009 | Image-gen default off on non-GPU + dreamforge network | Compose fix |
| 25 | #1004 | Skip compose.local.yaml on Apple Silicon | macOS fix |
| 26 | #1005 | macOS install polish | macOS fix |
| 27 | #1013 | DREAM_AGENT_KEY lifecycle on macOS | macOS fix |
| 28 | #1012 | Windows env result hash trim | Windows fix; depends on #996 |
| 29 | #996 | Generate DREAM_AGENT_KEY in Windows installer | Windows fix |
| 30 | #1015 | Dashboard template picker defensive fixes | Frontend fix |
| 31 | #1014 | Doctor extension diagnostics test fix | Test fix |
| 32 | #1020 | Apple Silicon GPU backend test coverage | Test addition |
| 33 | #1019 | Setup wizard sentinel contract + tests | Test + fix |
| 34 | #1018 | BATS regression shield for dream-cli | Test addition |
| 35 | #1003 | Sentinel-based setup wizard success detection | Setup fix |
| 36 | #1026 | Pre-mark setup wizard complete on install | Setup fix |
| 37 | #1025 | Wire Apple Silicon into /api/gpu/detailed | API fix |
| 38 | #1021 | Start extension sidecars during install | Install fix |
| 39 | #1022 | Async hygiene in extensions router | API fix |
| 40 | #1023 | SIGPIPE-safe first-line selection | Shell fix |
| 41 | #1024 | Array-expand COMPOSE_FLAGS for SC2086 | Shell fix |
| 42 | #1028 | Raise healthcheck start_period from 120s to 600s | Embeddings fix |
| 43 | #1032 | Mirror manifest depends_on for anythingllm/localai/continue | Extensions fix |
| 44 | #1033 | Align librechat MONGO_URI guard; remove :? from jupyter | Extensions fix |
| 45 | #1034 | Piper-audio healthcheck timeout gap; publish milvus health port | Extensions fix |

## Phase 4: Documentation & CI (PRs 46-55)

| Order | PR | Title | Rationale |
|-------|-----|-------|-----------|
| 46 | #1055 | Development workflow guide for dashboard-api | Documentation |
| 47 | #1053 | CI: filesystem-write gate for openclaw | CI addition |
| 48 | #1052 | Structural guard for langfuse setup_hook | Test guard |
| 49 | #1054 | Require deployable compose.yaml for installable check | Validation |
| 50 | #1049 | Convert jupyter command to exec-form list | Extensions fix |
| 51 | #1048 | Replace backticks with single quotes in env-generator | macOS fix |
| 52 | #1047 | Use 127.0.0.1 in langfuse healthcheck URLs | Extensions fix |
| 53 | #1046 | Bind Next.js 16 to 0.0.0.0 inside container | Extensions fix |
| 54 | #1040 | Chown postgres/clickhouse data dirs to image uids | Extensions fix |
| 55 | #1036 | Remove community privacy-shield (dead code) | Cleanup |

## Phase 5: Small Independent Fixes (PRs 56-65)

| Order | PR | Title | Rationale |
|-------|-----|-------|-----------|
| 56 | #1051 | Hoist yaml import, guard empty manifests | Resolver fix |
| 57 | #1029 | Dedupe override.yml; apply gpu_backends filter | Resolver fix |
| 58 | #1027 | Bind community extension ports via ${BIND_ADDRESS} | Extensions fix |
| 59 | #992 | Add OPENCLAW_TOKEN placeholder to .env.example | Config fix |
| 60 | #974 | Use $DOCKER_CMD for DreamForge restart | Windows fix |
| 61 | #1043 | Custom menu's 'n' answers not disabling services | Installer fix |
| 62 | #1042 | Redacted diagnostics bundle generator | Feature addition |
| 63 | #991 | Bump claude-code-action (superseded by #983) | REJECT |
| 64 | #990 | Bump github-script (superseded by #983) | REJECT |
| 65 | #1017 | Linux host-agent fallback docs | Documentation |

## Phase 6: Large PRs Requiring Judgment (PRs 66-75)

These PRs need maintainer review before merging.

| Order | PR | Title | Verdict | Rationale |
|-------|-----|-------|---------|-----------|
| 66 | #750 | AMD Multi-GPU Support | REVISE | High value for AMD partnership; needs sign-off |
| 67 | #364 | Dashboard API settings, voice runtime, diagnostics | REVISE | 158k lines; needs scope review |
| 68 | #983 | P2P GPU deploy toolkit for Vast.ai | REVISE | 9.7k lines; needs scope reduction |
| 69 | #973 | Sync documentation with codebase | REVISE | 1.2k lines; needs verification |
| 70 | #966 | Sync Windows and macOS support docs | REVISE | 4.5k lines; needs AMD review |
| 71 | #959 | Address audit findings | REVISE | 4.5k lines; needs scope review |
| 72 | #961 | Mobile paths for Android Termux and iOS a-Shell | REJECT | Out of scope |
| 73 | #351 | Comprehensive input validation tests | REJECT | Superseded by #364 |
| 74 | #716 | Sensible defaults for required env vars | REJECT | Superseded by #364 |
| 75 | #1037 | Expandable error text + poll recovery | REJECT | Superseded by #1045 |

## Merge Strategy

1. **Merge Phase 1-5 in order.** These 65 PRs are merge-ready and follow dependency chains.
2. **Review Phase 6 with maintainer.** The 10 revise/reject PRs need human judgment.
3. **Close rejected PRs with explanations.** Each reject has a documented reason.
4. **Request revisions for revise PRs.** Each revise has specific guidance.

## Estimated Effort

- **Phase 1-5:** ~2 hours (59 PRs, mostly small, well-documented)
- **Phase 6:** ~4 hours (10 PRs, need maintainer review)
- **Total:** ~6 hours to clear the backlog
