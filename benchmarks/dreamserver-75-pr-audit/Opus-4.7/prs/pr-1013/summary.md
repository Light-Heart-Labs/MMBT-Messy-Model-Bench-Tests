# PR #1013 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-agent-key): complete DREAM_AGENT_KEY lifecycle on macOS + docs

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Two related gaps in the `DREAM_AGENT_KEY` lifecycle (the independent 32-byte hex secret introduced by PR #979):

1. **`.env.example`** — adds a commented documentation entry for `DREAM_AGENT_KEY` next to the existing `DASHBOARD_API_KEY` entry, with a generation hint and a warning that rotation breaks host-agent authentication.
2. **macOS `installers/macos/lib/env-generator.sh`** — closes the upgrade gap: pre-PR-#979 installs that re-run the installer without `--force` previously skipped `DREAM_AGENT_KEY` entirely. The host agent then fell back to `DASHBOARD_API_KEY`, defeating #979's intent of making the two secrets independent. Fix adds an idempotent upsert inside the existing early-return block.

## Why
After PR #979 made `DREAM_AGENT_KEY` a distinct secret from `DASHBOARD_API_KEY`, the lifecycle was only complete on Linux (`installers/phases/06-directories.sh:208` — `_env_get`-or-generate). Windows landed in a separate PR. macOS was left with an inconsistency: fresh installs generated the key (via the heredoc `ENVEOF` path), but reinstalls/upgrades skipped the upsert and left pre-#979 installs without it. `.env.example` also never mentioned the key, making it invisible to anyone reading the example config.

## How
- `.env.example`: one commented documentation line inserted between the existing `# DASHBOARD_API_KEY=` and the Qdrant section. Matches the style of surrounding commented-key entries.
- `env-generator.sh`: inside the `if [[ -f "$env_path" ]] && [[ "$force  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
