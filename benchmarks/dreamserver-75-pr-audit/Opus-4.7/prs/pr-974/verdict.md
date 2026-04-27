# PR #974 — Verdict

> **Title:** fix(bootstrap): use $DOCKER_CMD for DreamForge restart
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/bootstrap-bare-docker`
> **Diff:** +3 / -3 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/974

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Three-line consistency fix in `dream-server/scripts/bootstrap-upgrade.sh:464-471`. Replaces bare `docker restart`, bare `docker ps`, and bare `docker compose up -d` with `$DOCKER_CMD restart`, `$DOCKER_CMD ps`, and `$DOCKER_COMPOSE_CMD up -d`. The rest of the file already uses `$DOCKER_CMD` consistently; these three were the only stragglers. On Linux installs that need `sudo docker`, the bare invocations would silently fail (the `|| log "WARNING: ..."` swallows the permission error). The PR description says only one line changes; the diff shows three, including a tasteful upgrade of `docker compose ... openclaw` to `$DOCKER_COMPOSE_CMD`. Net behavior: DreamForge and OpenClaw now actually restart on `sudo docker` Linux installs after a bootstrap-to-full model swap.

## Findings

- **Pre-existing `2>&1 || log "WARNING..."` is not a regression.** The PR keeps the existing pattern of routing failure into a `log` warning. This is the project's "don't crash bootstrap if a non-essential service fails" pattern; review.md and CLAUDE.md tolerate it for restart-style operations during phased install. The PR doesn't add any new silent catches; it just makes the underlying command actually reach Docker.
- **Single-line change. Verified against the diff.** No follow-up needed beyond merge.

## Cross-PR interaction

- No file overlap with the other 16 PRs in this batch.
- `bootstrap-upgrade.sh` is not in any of the cross-PR conflict clusters listed in `analysis/dependency-graph.md`.

## Trace

- `dream-server/scripts/bootstrap-upgrade.sh:464` — `docker restart dream-dreamforge` → `$DOCKER_CMD restart dream-dreamforge`.
- `dream-server/scripts/bootstrap-upgrade.sh:469` — `docker ps --filter ...` → `$DOCKER_CMD ps --filter ...`.
- `dream-server/scripts/bootstrap-upgrade.sh:472` — `docker compose ... up -d --force-recreate openclaw` → `$DOCKER_COMPOSE_CMD ... up -d --force-recreate openclaw`.
