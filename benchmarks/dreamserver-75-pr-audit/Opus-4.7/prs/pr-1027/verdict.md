# PR #1027 — Verdict

> **Title:** fix(extensions): bind community extension ports via ${BIND_ADDRESS}
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/community-extensions-bind-address`
> **Diff:** +87 / -35 across 31 file(s) · **Risk tier: Low (score 8/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1027

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 1 | _see review.md_ |
| D — Blast radius | 2 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **8** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Mechanical sweep applying the canonical `${BIND_ADDRESS:-127.0.0.1}` pattern (`upstream-context.md` §7) to 35 port-binding lines across 29 community extension compose files. **Default is loopback** — exactly the policy from `upstream-context.md` §6. Healthcheck `test:` URLs (container-internal loopback) are correctly preserved. The new `tests/test-bind-address-sweep.sh` regression test greps for bare `127.0.0.1:` on `ports:` lines and is wired into `make test` (and inherited by `gate:`), giving the policy a static enforcement gate going forward.

## Findings

- **Loopback-default verified.** Every modified line uses `${BIND_ADDRESS:-127.0.0.1}` — no bare `0.0.0.0`, no policy regression. Confirmed across all 29 services including the sensitive ones (privacy-shield, gitea SSH, frigate RTSP/WebRTC) which the PR body correctly flags as opt-in only.
- **Regression test is correct.** `tests/test-bind-address-sweep.sh:36` uses `grep -REn '^\s*-\s*"?127\.0\.0\.1:'` which matches `ports:` list entries (line-anchored at `-`) but skips healthcheck `test:` blocks. Pattern is bidirectional-tested per PR body.
- **Frigate UDP/TCP ports** (`frigate/compose.yaml:10-13`) get the same treatment for both transports — correct, as both are camera-stream surfaces.

## Cross-PR interaction

- Per `analysis/dependency-graph.md` Cluster context, this is in the disjoint extension cluster (#1027, #1028, #1029, #1032, #1033, #1034). No file-level overlap with the host-agent or dashboard-api clusters.
- Aligns with #988 (loopback bind for llama-server + host agent) — same security policy, different code surface (community extensions vs. core).
- Touches `Makefile` `test:` target — no other open PR in this batch modifies that target, so no rebase risk.

## Trace

- `Makefile:36-38` — wires `test-bind-address-sweep.sh` into `test` target
- `tests/test-bind-address-sweep.sh:1-49` — new regression guard (greps `ports:` only, excludes `test:`)
- 29 `resources/dev/extensions-library/services/*/compose.yaml` — substitution applied uniformly
- `frigate/compose.yaml:10-13`, `gitea/compose.yaml:28-29`, `weaviate/compose.yaml:21-22`, `text-generation-webui/compose.yaml:11-12` — multi-port services (all four transformed)
