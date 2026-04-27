# PR #973 — Verdict

> **Title:** docs: sync documentation with codebase after 50+ merged PRs
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `docs/sync-documentation-with-codebase`
> **Diff:** +376 / -115 across 13 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/973

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Big but mechanical: rewrites stale docs across 13 files to match the post-50-PR shipped behavior. Spot-checked the load-bearing claims: `QUICKSTART.md` and `README.md` tier tables now show `qwen3.5-9b` / `qwen3-30b-a3b` in line with `installers/lib/tier-map.sh`; `SECURITY.md:79-103` documents the `DREAM_AGENT_BIND` policy as actually implemented (loopback on macOS/Windows; auto-detect on Linux); `MODE-SWITCH.md:30-115` adds the lemonade auto-configured mode; `POST-INSTALL-CHECKLIST.md` replaces a 22-line skeleton with executable `dream` commands; new `extensions/services/langfuse/README.md` (116 lines) matches the manifest port `3006` and listed env keys. Touches `.env.example` to document a commented-out `LLAMA_CPU_LIMIT`. No production code changes.

## Findings

- **Single byte-count fix (root README.md) and one new admin-bind section (SECURITY.md) are the load-bearing parts.** The Apple Silicon "16-24 GB → 4B → 9B" correction at `README.md:188` matches the rest of the table and `tier-map.sh`'s actual mapping. The new "Host Agent Network Binding" subsection at `SECURITY.md:79-103` documents the same `DREAM_AGENT_BIND` policy that PR #988 ships in code — these belong together; #973's docs version is fine on its own and accurate to the post-#988 state.
- **Heavy textual overlap with PR #966 in the same area but different files.** PR #966 rewrites `WINDOWS-INSTALL-WALKTHROUGH.md`; this PR rewrites `WINDOWS-QUICKSTART.md`. No file collision. Whichever lands first has zero impact on the other.
- **`.env.example` change is a comment-only addition.** Adds three lines documenting `LLAMA_CPU_LIMIT` (commented out, no default change). Per the project rule "schema changes must update both `.env.schema.json` and `.env.example`" — this is documentation only, not a new key, so no schema update needed. Verified the `LLAMA_CPU_LIMIT` it documents is read by `installers/macos/docker-compose.macos.yml` (already in main).
- **Convention adherence:** No `eval`, no new `2>/dev/null`, no `|| true`, no retry chains, no port bindings touched, no `installers/lib/` files. Pure docs.

## Cross-PR interaction

- Overlaps with PR #966 (boffin-dmytro Windows docs) — different files, no conflict.
- Overlaps with PR #988 (loopback bind) — #973's `SECURITY.md:79-103` documents post-#988 behavior. **Should land after #988** so the docs don't promise a behavior the code doesn't yet have. (Same gating principle as PR #1017, per `analysis/dependency-graph.md` Cluster 6.)
- No conflict with PR #992 (`OPENCLAW_TOKEN` in `.env.example`) — both add to `.env.example` but in different sections.
- No conflict with PR #994 (schema-driven masking) — that PR touches `.env.schema.json`; this PR touches `.env.example` for a different key.

## Trace

- `README.md:188` — Apple Silicon 16-24GB tier "4B" → "9B" (matches `tier-map.sh`).
- `dream-server/SECURITY.md:79-103` — new `DREAM_AGENT_BIND` documentation block (load-bearing, post-#988).
- `dream-server/docs/MODE-SWITCH.md:30, 90-115` — lemonade-auto-configured-mode section.
- `dream-server/docs/POST-INSTALL-CHECKLIST.md` — full rewrite from unchecked-checklist skeleton to numbered command-driven verification.
- `dream-server/extensions/services/langfuse/README.md` — new (116 lines), matches manifest.
- `dream-server/.env.example:258-260` — `LLAMA_CPU_LIMIT` doc-comment (no schema change needed).
