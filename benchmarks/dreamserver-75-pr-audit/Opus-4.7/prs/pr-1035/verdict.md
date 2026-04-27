# PR #1035 — Verdict

> **Title:** fix(openclaw): trigger open-webui recreate on install; simplify volume layout
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/openclaw-recreate-overlay`
> **Diff:** +117 / -8 across 5 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1035

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

**MERGE.** Two coherent fixes for openclaw. (1) New `_post_install_core_recreate(service_id)` helper at `bin/dream-host-agent.py:272-290` recreates `open-webui` after openclaw installs so the overlay's `OPENAI_API_BASE_URLS` + `OPENAI_API_KEYS` actually reach the running container — a real bug since `up -d --no-deps openclaw` doesn't pick up env-overlay changes for already-running core services. Hardcoded to openclaw is the right call; introducing a manifest-level `post_install_requires_recreate` field for one use case would be over-engineering. (2) Drops the `openclaw-home` named Docker volume entirely — verified empirically that openclaw only writes regenerated content under `/home/node/.openclaw/`, so the named volume held nothing worth persisting.

## Findings

- **The broad `except Exception` at `:1188-1193` is acceptable** here — it's wrapped with `logger.exception(...)` (stack trace preserved, not silent), runs in a daemon thread post-success, and the PR body explicitly justifies the triple-layer failure isolation. The original install must not fail on recreate hiccups (openclaw is already up; the overlay just won't take effect until manual restart). Aligns with `upstream-context.md` §8 "narrow exceptions at I/O boundaries" interpretation.
- **Migration note required:** existing installs will leave an orphaned `openclaw-home` Docker volume. PR body documents `docker volume rm openclaw-home` as the manual reclaim. Worth surfacing in release notes.
- **Test layout includes a source-grep guard** (`tests/test_host_agent.py:341-352`) to lock the call ordering — `_post_install_core_recreate` must run *after* the `"started"` progress write. Brittle but matches the file's prevailing pattern and pins the contract.

## Cross-PR interaction

- Per `analysis/dependency-graph.md` Cluster 2 ordering: #988 → #1021 → #1030 → #1050 → #1057 → **#1035**. **Soft conflict with #1030** at the `_handle_install` post-success block — this PR adds Step 5 right after #1030's Step 4 (state-poll). Trivial textual merge.
- **Soft conflict with #1021** on `_handle_install` argv area — disjoint regions but adjacent commits. Mergeable.
- Aligns with #988 (security/loopback for openclaw was already addressed via #67); this PR only touches volume layout and post-install hook, not bindings.

## Trace

- `bin/dream-host-agent.py:272-290` — new `_post_install_core_recreate` helper
- `bin/dream-host-agent.py:1185-1193` — call site after `"started"` progress write
- `extensions/services/openclaw/compose.yaml:27` — drop `openclaw-home` mount
- `extensions/services/openclaw/compose.yaml:58-60` — drop `volumes:` block
- `extensions/services/openclaw/README.md:47` — table row removed
- `installers/phases/06-directories.sh:149-153` — comment updated to reflect ephemeral overlay
- `tests/test_host_agent.py:288-353` — 5 new tests + source-grep ordering guard
