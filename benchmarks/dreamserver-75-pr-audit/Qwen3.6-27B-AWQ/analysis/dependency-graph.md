# PR Dependency & Conflict Graph

## Methodology

Built by analyzing file-level overlaps across all 75 open PRs. Two PRs are considered to have a **file conflict** if they modify the same file. A **dependency** exists when PR A must be merged before PR B can be cleanly merged (B references code/behavior introduced by A). A **supersession** exists when PR A makes PR B obsolete.

## Critical Conflict Clusters

### Cluster 1: Extensions Library (PRs #351, #364, #716, #1027, #716)

**Files affected:** 700+ files in `resources/dev/extensions-library/`

- **PR #351** (reo0603): 864 files, 158k lines — comprehensive test suite for extensions
- **PR #364** (championVisionAI): 864 files, 158k lines — dashboard-api settings, voice runtime, diagnostics
- **PR #716** (Arifuzzamanjoy): 736 files, 152k lines — sensible defaults for required env vars
- **PR #1027** (yasinBursali): 31 files — bind address sweep for community extensions

**Conflict:** All four touch the same extension compose.yaml and manifest.yaml files. PRs #351 and #364 are near-duplicates (same file count, same services). PR #716 overlaps with both.

**Resolution:** PR #351 and #364 appear to be competing implementations of similar extensions-library work. PR #716 (env defaults) is the most focused and has the clearest scope. PR #1027 (bind address) is a follow-up to #964 and is independent.

### Cluster 2: Host Agent (PRs #1057, #1050, #1039, #1038, #1035, #1030, #988)

**File:** `dream-server/bin/dream-host-agent.py`

- **PR #1057:** stderr truncation fix, narrow pull, catalog error handling
- **PR #1050:** Non-POSIX filesystem detection, Docker Desktop sharing verification
- **PR #1039:** Retry install failure through hook + progress path
- **PR #1038:** Honor pre_start return, surface post_start failure
- **PR #1035:** openclaw recreate on install, volume layout simplification
- **PR #1030:** Install flow — built-in hooks, bind-mount anchor, post-up state
- **PR #988:** Security — bind llama-server and host agent to loopback

**Conflict:** All modify `dream-host-agent.py`. PRs #1057 and #1050 both modify `_precreate_data_dirs`. PR #1030 and #1057 both modify the install flow.

**Resolution:** These are all from yasinBursali and are designed to be complementary. Merge order matters:
1. PR #988 (security baseline) first
2. PR #1030 (install flow foundation)
3. PR #1050 (filesystem detection)
4. PR #1057 (runtime hygiene)
5. PR #1039 (retry logic)
6. PR #1038 (hook handling)
7. PR #1035 (openclaw-specific)

### Cluster 3: Dashboard API Extensions Router (PRs #1056, #1045, #1044, #1038, #1037, #1022)

**File:** `dream-server/extensions/services/dashboard-api/routers/extensions.py`

- **PR #1056:** Catalog timeout, orphaned whitelist, GPU passthrough scan
- **PR #1045:** Route extension config sync through host agent
- **PR #1044:** Accept ${VAR:-127.0.0.1} in compose port-binding scan
- **PR #1038:** Honor pre_start return, surface post_start failure
- **PR #1037:** Expandable error text + poll recovery
- **PR #1022:** Async hygiene in routers/extensions.py

**Conflict:** All modify the same router file. PR #1037 and #1045 both add "unhealthy" status handling.

**Resolution:** PR #1037 is a subset of #1045's changes. Merge #1045 and reject #1037 as superseded.

### Cluster 4: dream-cli (PRs #1016, #1011, #1008, #1007, #1006, #1002, #1000, #999, #998, #997, #994, #993)

**File:** `dream-server/dream-cli`

- **PR #1016:** Apple GPU output polish + compose wrapper SIGINT
- **PR #1011:** Bash 3.2 guard + dream-cli validate routing
- **PR #1008:** Guard .env grep pipelines against pipefail
- **PR #1007:** Double-quote tmpdir in gpu_reassign RETURN trap
- **PR #1006:** Route log() and warn() to stderr
- **PR #1002:** Enable set -u + guards for conditional variables
- **PR #1000:** --json flag on list/status
- **PR #999:** Apple Silicon coverage for gpu subcommands
- **PR #998:** pipefail + surface LLM failures + exit-code contract
- **PR #997:** Pre-validate 'dream shell' service + Docker daemon preflight
- **PR #994:** Schema-driven secret masking + macOS Bash 4 validation
- **PR #993:** Color-escape + table-separator + NO_COLOR spec

**Conflict:** All modify `dream-cli`. PR #998 (pipefail) and #1002 (set -u) interact — both enable stricter bash modes. PR #1008 depends on #998 being merged first.

**Resolution:** Merge in dependency order:
1. PR #998 (pipefail baseline)
2. PR #1002 (set -u)
3. PR #1008 (pipefail hygiene follow-up)
4. PR #1006 (stderr routing)
5. PR #1007 (trap quoting)
6. PR #994 (secret masking)
7. PR #993 (visual polish)
8. PR #999 (Apple Silicon)
9. PR #1000 (json flag)
10. PR #997 (shell validation)
11. PR #1016 (Apple GPU polish)
12. PR #1011 (Bash 3.2)

### Cluster 5: Compose Resolver (PRs #1051, #1029, #1004, #1024)

**File:** `dream-server/scripts/resolve-compose-stack.sh`

- **PR #1051:** Hoist yaml import, guard empty manifests, align user-ext loop
- **PR #1029:** Dedupe override.yml, apply gpu_backends filter to user-extensions
- **PR #1004:** Skip compose.local.yaml on Apple Silicon
- **PR #1024:** Array-expand COMPOSE_FLAGS for SC2086 + glob safety

**Conflict:** PRs #1051 and #1029 both modify the user-extensions loop. PR #1051 supersedes #1029's user-ext changes.

**Resolution:** Merge #1051 (supersedes #1029's user-ext work). Merge #1029 for the override.yml dedup (independent). Merge #1004 (Apple Silicon fix, independent). Merge #1024 (shell safety, independent).

### Cluster 6: Installer (PRs #1050, #1043, #1026, #974)

- **PR #1050:** Block non-POSIX INSTALL_DIR + verify Docker Desktop sharing
- **PR #1043:** Custom menu's 'n' answers not disabling services (y-coffee-dev)
- **PR #1026:** Pre-mark setup wizard complete on successful install
- **PR #974:** Use $DOCKER_CMD for DreamForge restart

**Conflict:** PR #1050 and #1043 both modify installer preflight logic.

**Resolution:** Independent changes, no direct conflict. Merge in any order.

### Cluster 7: Windows (PRs #1012, #996, #974, #959)

- **PR #1012:** Trim dead fields from New-DreamEnv return hash
- **PR #996:** Generate DREAM_AGENT_KEY in installer env-generator.ps1
- **PR #974:** Use $DOCKER_CMD for DreamForge restart
- **PR #959:** Address audit findings — Windows docs, Token Spy auth

**Conflict:** PR #996 and #1012 both modify `env-generator.ps1`. PR #1012 trims fields that #996 adds.

**Resolution:** Merge #996 first (adds DREAM_AGENT_KEY), then #1012 (trims dead fields, keeping the new one).

## Supersession Map

| Superseded PR | Superseding PR | Reason |
|---|---|---|
| #1037 | #1045 | #1045 includes all of #1037's "unhealthy" status changes plus more |
| #1029 (user-ext part) | #1051 | #1051's user-ext loop is more comprehensive |
| #351 | #364 | Near-duplicate extensions library work; #364 has broader scope |
| #716 | #364 | #364 includes env defaults work |
| #991 | #983 | #983 includes the same claude-code-action bump |
| #990 | #983 | #983 includes the same github-script bump |

## Dependency Chains

### Chain A: Security → Host Agent → Extensions
```
#988 (loopback binding)
  → #1030 (install flow)
    → #1050 (filesystem detection)
      → #1057 (runtime hygiene)
        → #1039 (retry logic)
          → #1038 (hook handling)
            → #1035 (openclaw recreate)
```

### Chain B: CLI Foundation → CLI Features
```
#998 (pipefail)
  → #1002 (set -u)
    → #1008 (pipefail hygiene)
      → #1006 (stderr routing)
        → #1007 (trap quoting)
          → #994 (secret masking)
            → #993 (visual polish)
              → #999 (Apple Silicon)
                → #1000 (json flag)
                  → #997 (shell validation)
                    → #1016 (Apple GPU polish)
                      → #1011 (Bash 3.2)
```

### Chain C: AMD Multi-GPU
```
#750 (AMD Multi-GPU) — standalone, no dependencies
  → #1032 (depends_on mirror for anythingllm/localai/continue) — compatible
```

## Cross-PR Patterns

1. **yasinBursali dominance:** 63/75 PRs from a single contributor. These are generally high-quality but create merge ordering complexity.
2. **Extensions library bloat:** PRs #351, #364, #716 each add 150k+ lines. These need maintainer judgment on whether the extensions library should be pruned before merging.
3. **AMD partnership relevance:** PR #750 (AMD Multi-GPU) is the single highest-value PR for the AMD developer program partnership.
4. **Security cluster:** PRs #988, #994, #1010, #1050 all address security/credential handling. These should be prioritized.
