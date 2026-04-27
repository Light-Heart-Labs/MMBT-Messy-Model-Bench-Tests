# PR #1057 — Verdict

> **Title:** fix(host-agent): runtime hygiene — narrow pull, surface failures, normalize bind volumes
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/host-agent-runtime-hygiene`
> **Diff:** +73 / -13 across 1 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1057

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

**MERGE**

Seven scoped hygiene edits, each addressing a real failure-mode-of-the-failure-mode in the host agent. (1) Narrowing `docker compose pull` flags so a `${VAR:?}` in an unrelated extension's compose doesn't kill the target's pull (diff.patch:38-66) — `pull_flags` filters out `-f` entries pointing at *other* extensions while leaving `up`'s full flags intact for cross-service `depends_on`. Conservative: paths that can't be resolved stay in the list. (2) Three `stderr[:N]` → `stderr[-N:]` flips (diff.patch:28, 77, 86) — Docker's real error is at the end of stderr, not the head. (3) `_write_model_status` `except OSError: pass` → `logger.warning` (diff.patch:158-161) — preserves activate-flow continuation but surfaces to journal. (4) `_recreate_llama_server` raises after logging (diff.patch:147), turning a 5-minute health-check hang into a fast fail. (5) Distinguishes catalog-unavailable (500) from policy-denied (403) in `_handle_model_download` via `catalog_ok` sentinel (diff.patch:118, 123, 132-137). (6+7) `_precreate_data_dirs` handles dict-form `{type: bind, source: ./foo, target: /bar}` (diff.patch:10-14) and skips non-pre-expanded sources `~/`, `$VAR`, backtick, backslash (diff.patch:18-20).

## Findings

- **Behavior change** (called out in PR body): `_handle_model_download` now returns 500 instead of 403 for missing/unreadable catalog. Asymmetry with `_handle_model_list` (which returns 200 + empty catalog as browse semantics) is documented inline. Defensible distinction.
- The dict-form volume normalize is the same territory as #1039/#1045's `_precreate_data_dirs` widening but takes a different angle (dict-form support, not the `./data/` filter widening). They'll need rebase coordination but no semantic conflict.
- `_recreate_llama_server` is reachable on Linux native via the `_compose_restart_llama_server` no-`.compose-flags` fallback (per PR body) — the raise covers both Windows/in-container and that under-documented Linux path.

## Cross-PR interaction

- Same `bin/dream-host-agent.py` as #1039, #1040, #1045 — touches different functions for the most part. `_precreate_data_dirs` in this PR adds dict-form + safety filter; #1039/#1040/#1045 widen the `./data/` filter. Both changes layer cleanly but need rebase merge.
- Per the cluster ordering `#988 → #1021 → #1030 → #1050 → #1057 → #1035 → #1040 → #1045 → #1039`, this lands ahead of the others.

## Trace

- `bin/dream-host-agent.py:202-220` — dict-form bind + safety filter in `_precreate_data_dirs`
- `bin/dream-host-agent.py:1140-1180` — narrow `pull_flags` + `_is_other_ext_compose`
- `bin/dream-host-agent.py:1146, 1158, 1198` — three `stderr[-N:]` tail-truncation flips
- `bin/dream-host-agent.py:1233-1247, 1313-1357` — model-library catalog 500-vs-403 distinction
- `bin/dream-host-agent.py:2202-2204` — `_recreate_llama_server` raise
- `bin/dream-host-agent.py:2220-2225` — `_write_model_status` logger.warning
