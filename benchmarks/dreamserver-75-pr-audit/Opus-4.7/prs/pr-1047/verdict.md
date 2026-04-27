# PR #1047 — Verdict

> **Title:** fix(langfuse): use 127.0.0.1 in healthcheck URLs
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/langfuse-healthcheck-loopback`
> **Diff:** +4 / -4 across 1 file(s) · **Risk tier: Trivial (score 1/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1047

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

**MERGE**

Pure convention alignment. busybox `wget` in Alpine resolves `localhost` → `::1` first, the bridge network has no IPv6 stack, and busybox doesn't fall back to IPv4 — so langfuse-worker hangs in `(unhealthy)` until the deadline. All four healthcheck URLs (diff.patch:9, 18, 27, 36) are inside the container; nothing affects host-side binding. The PR correctly **leaves line 30 `NEXTAUTH_URL` untouched** (a browser-evaluated OAuth callback URL — changing it would break login). The other 12 built-in extensions already use 127.0.0.1 in healthchecks; this brings langfuse into line.

## Findings

- 4-line surgical change across web, worker, clickhouse, minio healthchecks. Each replaces `localhost` with `127.0.0.1` only in the wget/curl probe arg.
- File is `compose.yaml.disabled` — only takes effect after `dream enable langfuse`, so existing healthy installs aren't disrupted on restart.

## Cross-PR interaction

- No file overlaps with other open PRs. Pairs sympathetically with #1040 (langfuse setup hook) and #1052 (langfuse test) but doesn't depend on either.

## Trace

- `extensions/services/langfuse/compose.yaml.disabled:57` — langfuse-web wget
- `extensions/services/langfuse/compose.yaml.disabled:117` — langfuse-worker wget
- `extensions/services/langfuse/compose.yaml.disabled:188` — clickhouse wget (CMD exec-array)
- `extensions/services/langfuse/compose.yaml.disabled:256` — minio curl
