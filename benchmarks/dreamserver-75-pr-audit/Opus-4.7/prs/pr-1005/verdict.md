# PR #1005 — Verdict

> **Title:** fix(macos): install-time polish — DIM constant, busybox pin, healthcheck rewrite
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/macos-install-polish`
> **Diff:** +35 / -17 across 3 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1005

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **4** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Three independent macOS-only fixes that each stand on their own:
(1) adds the missing `DIM` color at `installers/macos/lib/constants.sh:82`,
fixing the `unbound variable` crash at the final summary banner under `set -u`;
(2) pins `busybox:latest` → `busybox:1.36.1` at
`installers/macos/docker-compose.macos.yml:9,18` for reproducibility on the
active `llama-server-ready` sidecar; (3) rewrites the phase-6 healthcheck loop
in `installers/macos/install-macos.sh:1053-1099` to use
`docker inspect --format '{{.State.Health.Status}}'` for Docker services and
extends `MAX_ATTEMPTS` to 90 (180s), eliminating the false
"not responding after 30 attempts" warnings on cold installs.

## Findings

- The healthcheck rewrite preserves the forgiving `warn` + `ALL_HEALTHY=false`
  semantics on timeout (no `exit`), so a slow service still completes the
  install rather than aborting. Good restraint.
- All `localhost` URLs become `127.0.0.1` per project convention, sidestepping
  IPv6 `::1` resolution quirks on Docker Desktop for Mac. Cosmetic but correct.
- The `2>/dev/null || echo "missing"` on the new `docker inspect` (line 1071)
  is a pre-existing pattern in the same loop and is narrowly scoped to the
  one command — not a regression on the broad-catch rule.
- Scope is genuinely macOS-only. No Linux/Windows files touched.

## Cross-PR interaction

- No file overlap with other PRs in this batch. The only macOS install-flow
  PR overlap in the open queue is #988 (host-agent loopback), which touches
  different lines in `install-macos.sh`. Trivial textual conflict at most.

## Trace

- `dream-server/installers/macos/lib/constants.sh:82` — `DIM` added
- `dream-server/installers/macos/docker-compose.macos.yml:9,18` — busybox pin
- `dream-server/installers/macos/install-macos.sh:1053-1099` — healthcheck loop
- `installers/lib/constants.sh:52` — shared palette source for `DIM` (not sourced
  by macOS installer; rationale for the local copy is correct)
