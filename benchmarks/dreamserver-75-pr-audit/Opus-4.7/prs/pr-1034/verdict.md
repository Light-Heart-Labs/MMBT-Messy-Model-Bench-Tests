# PR #1034 — Verdict

> **Title:** fix(extensions): piper-audio healthcheck timeout gap; publish milvus health port
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/community-healthcheck-reliability`
> **Diff:** +2 / -1 across 2 file(s) · **Risk tier: Trivial (score 1/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1034

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 0 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **1** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Two minimal fixes: (1) `piper-audio/compose.yaml:34` drops the healthcheck `timeout` from 30s to 10s — matching the inner `nc -w 1` probe's actual ~1s self-termination and giving idle space between the 30s `interval` ticks. (2) `milvus/compose.yaml:7` publishes the `9091` health port that was declared in the manifest but never bound to the host. The new line uses `${BIND_ADDRESS:-127.0.0.1}` (loopback default per `upstream-context.md` §6/§7), forward-compatible with #1027's BIND_ADDRESS sweep. Original chromadb item was dropped after runtime verification proved the existing probe is correct for the pinned `chromadb/chroma:1.5.3` image.

## Findings

- **Scope-shrink discipline is good.** PR body documents that chromadb was empirically disproven (image has full bash 5.2.37 with `/dev/tcp`; wget/curl/nc/python3 all absent — existing probe is the best available). Three-item issue → two confirmed fixes; the unverified item correctly dropped.
- **Latent dashboard-api gap noted in PR body** (`user_extensions.py:83-89` doesn't read `health_port` from manifest, unlike `config.py:136` for built-ins). Publishing 9091 here doesn't fix that — flagged correctly as separate work, not bundled.
- **The new milvus 9091 line uses `${BIND_ADDRESS:-127.0.0.1}`** while the existing 19530 line still has hardcoded `127.0.0.1` — that's #1027's job to sweep. Both PRs converge on the canonical pattern; ordering doesn't matter.

## Cross-PR interaction

- **Soft conflict with #1027** on `milvus/compose.yaml` `ports:` block. #1027 changes line 6 (existing 19530), this PR adds line 7 (new 9091). Textually adjacent but mergeable; whichever lands first, the other rebases trivially.
- Part of the disjoint extension-fixes group (#1027/#1028/#1029/#1032/#1033/**#1034**) — could collapse with #1032 + #1033 into a single sweep PR per dependency-graph suggestion.

## Trace

- `services/piper-audio/compose.yaml:34` — `timeout: 30s` → `10s`
- `services/milvus/compose.yaml:7` — new `"${BIND_ADDRESS:-127.0.0.1}:9091:9091"` port mapping
