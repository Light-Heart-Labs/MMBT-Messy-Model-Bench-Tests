# PR #1028 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(embeddings): raise healthcheck start_period from 120s to 600s

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Raise `start_period` on the `embeddings` extension healthcheck from `120s` to `600s`.

## Why
The Hugging Face TEI image downloads its model at first start. On slow connections a ~115 MB model (default `BAAI/bge-base-en-v1.5`) can exceed the existing 120s + 5x30s = 270s total grace window, making the container flip `unhealthy` while the download is still progressing, followed by restart-loop confusion on the dashboard.

## How
One-line edit to `dream-server/extensions/services/embeddings/compose.yaml:28`.

`start_period` is a grace window — Docker ignores failed checks inside it and flips to healthy on the first successful probe — so raising it does not slow down warm starts and does not mask true crash-loops (`restart: unless-stopped` still triggers on non-zero exit).

## Testing
- `docker compose config` parses the modified file cleanly.
- `scripts/validate-compose-stack.sh` passes (2 services, exit 0).
- `python3 -c "import yaml; yaml.safe_load(...)"` — YAML valid.
- `pre-commit` (gitleaks, private-key, large-file) passes.
- No env vars added, `.env.schema.json` untouched.

## Review
Critique Guardian APPROVED (no required changes).

## Platform Impact
- **macOS:** identical behavior (Docker Desktop); healthcheck semantics are engine-level, platform-neutral.
- **Linux:** identical behavior.
- **Windows (WSL2):** identical behavior.

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
