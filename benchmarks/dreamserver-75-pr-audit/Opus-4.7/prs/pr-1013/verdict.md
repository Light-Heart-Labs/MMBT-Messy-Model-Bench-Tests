# PR #1013 — Verdict

> **Title:** fix(dream-agent-key): complete DREAM_AGENT_KEY lifecycle on macOS + docs
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dream-agent-key-lifecycle`
> **Diff:** +8 / -0 across 2 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1013

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

**MERGE.** Adds five lines to `installers/macos/lib/env-generator.sh` (inside
the existing `[[ -f "$env_path" ]] && [[ "$force_overwrite" != "true" ]]`
early-return block) that idempotently upsert `DREAM_AGENT_KEY` when missing,
plus a three-line commented entry in `.env.example`. This closes the
upgrade gap left by #979: pre-#979 macOS installs that rerun the installer
without `--force` previously skipped `DREAM_AGENT_KEY` entirely, leaving the
host agent to fall back to `DASHBOARD_API_KEY` (which defeats the whole point
of #979 making the two secrets independent). Linux already had the equivalent
pattern at `installers/phases/06-directories.sh:208`; Windows landed in a
separate PR. This is the macOS catch-up.

## Findings

- The upsert is idempotent: `read_env_value` returns empty when the key
  is absent, so subsequent runs no-op. Fresh-install Path B (the heredoc that
  always writes the key) is unchanged. Three reasoning scenarios the body
  outlines (missing / empty / populated) all produce the right outcome.
- The body identifies a stale schema description at `.env.schema.json:269` —
  still says "falls back to `DASHBOARD_API_KEY` if unset" post-#979.
  Out-of-scope here, correctly noted as a follow-up.
- `.env.example` entry placement is consistent with the surrounding commented
  generator hints. Rotation warning is appropriately surfaced.

## Cross-PR interaction

- `.env.example` is also touched by #1017 (which has its own loopback-doc
  edit nearby) and #973 (post-merge sync). Different lines; mechanical
  textual conflict resolution.
- `installers/macos/lib/env-generator.sh` doesn't overlap with any other
  open PR in this batch.

## Trace

- `dream-server/installers/macos/lib/env-generator.sh:119-123` — idempotent
  upsert added inside the early-return block
- `dream-server/.env.example:148-150` — commented documentation entry
- `dream-server/installers/phases/06-directories.sh:208` — Linux precedent
  (referenced; unchanged)
- `dream-server/.env.schema.json:269` — stale description (out of scope,
  flagged for follow-up)
