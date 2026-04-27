# PR #997 — Verdict

> **Title:** fix(dream-cli): pre-validate 'dream shell' service + Docker daemon preflight
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dream-shell-pre-validation`
> **Diff:** +46 / -2 across 1 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/997

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Replaces an actual fallback chain with explicit branching, which is the correct direction per CLAUDE.md. Pre-PR: `docker exec -it "$container" /bin/bash || docker exec -it "$container" /bin/sh` — two-step retry on any exec failure (daemon down, container missing, or no bash binary). Post-PR `dream-cli:1099-1115`: one explicit service-ID validation against `SERVICE_IDS`, one explicit Docker-daemon preflight (`perl -e 'alarm 3; exec "docker", "info"'` for portable timeout), one explicit container-running check (`docker ps --format '{{.Names}}' | grep -qx "$container"`), one explicit bash-binary probe (`docker exec ... test -x /bin/bash`), then a non-fallback exec. Each failure now produces a precise error message instead of cascading mismatched Docker errors.

## Findings

- **This PR removes a `docker ... || docker ...` retry pattern, which is project-policy-aligned.** CLAUDE.md prohibits "retry/fallback chains"; the pre-PR code was exactly that pattern. The post-PR code is "probe then exec," which is not a retry — it's a pre-condition check. Correct direction.
- **`perl -e 'alarm 3; exec "docker", "info"'` is the portable-timeout idiom.** macOS doesn't ship `timeout(1)` in the base system, only via Homebrew coreutils. `perl` is in macOS base since 10.5 and on every supported Linux/WSL2 distro. The PR comment at `:1112` documents why — best-in-class.
- **The two `2>/dev/null` redirects on `docker info` and `docker ps` are scoped to detection probes**, not silent error-swallowing — the function `error`s with a precise message immediately on probe failure. CLAUDE.md tolerates `2>/dev/null` when the failure is the *signal*, which is the case here. Consistent with the existing `dream-cli` pattern.

## Cross-PR interaction

- Touches `dream-cli` — Cluster 1 conflict file. Per `analysis/dependency-graph.md`, sits at "step 6" (after #993, #994). Textual conflicts with later Cluster-1 PRs are mechanical.
- The new `sr_load` call at `:1083` ensures `SERVICE_IDS` is populated; this is a load-bearing change — service-registry helper functions like `sr_load` come from `installers/lib/service-registry.sh`. PR #1006 (log → stderr) and PR #1008 (pipefail grep guard) are foundation PRs, so this PR only depends on `sr_load` already being there. Verified — `sr_load` is in `main`.

## Trace

- `dream-server/dream-cli:1083` — `sr_load` populates `SERVICE_IDS` in current shell (replaces a subshell-loss bug per the body).
- `dream-server/dream-cli:1090-1097` — service-ID validation against the registry; pre-flight `error "Unknown service: ..."` instead of cascading Docker errors.
- `dream-server/dream-cli:1108-1115` — `perl alarm 3` Docker-daemon probe; container-running check.
- `dream-server/dream-cli:1118-1122` — bash-binary probe replaces `docker exec ... /bin/bash || docker exec ... /bin/sh` retry.
