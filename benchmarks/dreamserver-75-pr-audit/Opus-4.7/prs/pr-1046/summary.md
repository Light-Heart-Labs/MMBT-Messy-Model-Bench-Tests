# PR #1046 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(perplexica): bind Next.js 16 to 0.0.0.0 inside container

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Add `HOSTNAME=0.0.0.0` to the perplexica service environment so Next.js 16 binds the loopback interface inside the container.

## Why
The pinned `itzcrazykns1337/perplexica:slim-latest` image ships **Next.js 16.0.7**. Next 16 changed the standalone-server bind behaviour: it reads `process.env.HOSTNAME` (defaulting to the container's hostname / Docker bridge IP) and listens *only* on that interface. The healthcheck at `extensions/services/perplexica/compose.yaml:29` probes `http://127.0.0.1:3000/`, which always returns `ECONNREFUSED` because nothing is bound to loopback. The container ends up permanently `(unhealthy)` even though it serves traffic correctly via the bridge IP.

This is a real binding mismatch, not a probe mistake — commit `67a57973` (PR #977) intentionally moved the healthcheck to `127.0.0.1` to match the project-wide convention; the convention is correct, the upstream image's bind default is what's incompatible.

## How
Single-line addition to `extensions/services/perplexica/compose.yaml`:
```yaml
      - HOSTNAME=0.0.0.0
```
Placed after the existing `OPENAI_API_KEY` line in the env list (list-form `- KEY=VALUE`, matching `n8n/compose.yaml` and `searxng/compose.yaml` style).

The host-side `${BIND_ADDRESS:-127.0.0.1}:${PERPLEXICA_PORT:-3004}:3000` mapping is untouched, so the loopback default for host-side LAN exposure is preserved (LAN mode still requires the operator to opt in via `--lan` / dashboard / `BIND_ADDRESS=0.0.0.0` in `.env`).

## Testing
  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
