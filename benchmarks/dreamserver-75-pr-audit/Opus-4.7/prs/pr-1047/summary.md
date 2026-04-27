# PR #1047 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(langfuse): use 127.0.0.1 in healthcheck URLs

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Sweep the four healthcheck URLs in `extensions/services/langfuse/compose.yaml.disabled` from `localhost` to `127.0.0.1`. **Line 30 `NEXTAUTH_URL` is intentionally left untouched.**

## Why
busybox `wget` in Alpine resolves `localhost` → `::1` first. The container has no IPv6 stack on the bridge network, so the connection is refused and busybox `wget` gives up without retrying the IPv4 address. langfuse-worker reports `(unhealthy)` permanently as a result.

This is exactly the failure mode the project memory documents ("healthchecks must use `127.0.0.1`, not `localhost`"). The other 12 built-in extensions already follow this convention (n8n, searxng, embeddings, etc.); langfuse was an outlier. langfuse-web / clickhouse / minio currently report healthy because curl / the clickhouse image's wget handle the IPv4 fallback better — but they're one image-update away from regressing, so the sweep is preventive.

## How
Single-file edit to `extensions/services/langfuse/compose.yaml.disabled`:

| Line | Service | URL |
|---|---|---|
| 57 | langfuse (web) | `localhost:3000/api/public/health` → `127.0.0.1:3000/api/public/health` |
| 117 | langfuse-worker | `localhost:3030/api/health` → `127.0.0.1:3030/api/health` |
| 188 | langfuse-clickhouse | `localhost:8123/ping` → `127.0.0.1:8123/ping` (CMD exec-array form) |
| 256 | langfuse-minio | `localhost:9000/minio/health/live` → `127.0.0.1:9000/minio/health/live` (curl) |

**Line 30 `NEXTAUTH_URL: "http://localhost:${LANGFUSE_PORT:-30  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
