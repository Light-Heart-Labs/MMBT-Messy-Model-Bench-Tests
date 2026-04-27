# PR #973 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> docs: sync documentation with codebase after 50+ merged PRs

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary

Systematic audit of the last 50 merged PRs against all existing documentation revealed stale, contradictory, and missing docs. This PR fixes them:

- **WINDOWS-QUICKSTART.md**: Remove "Coming Soon — Preflight Checks Only" language (Windows has been fully supported since March 2026). Add real install flow, verified `dream.ps1` commands, and accurate installer flags
- **MODE-SWITCH.md**: Add lemonade mode section — auto-configured on AMD hardware, not user-switchable via `dream mode`
- **QUICKSTART.md / README.md**: Update all stale Qwen2.5 model names to Qwen3.5/Qwen3 matching current `tier-map.sh`
- **POST-INSTALL-CHECKLIST.md**: Rewrite 22-line skeleton (unchecked boxes, no commands) with real verification steps
- **SECURITY.md**: Add `DREAM_AGENT_BIND` / LAN access documentation with platform defaults
- **FAQ.md**: Add backup/restore, service templates, bootstrap fast-start, and expanded update/rollback docs
- **HOST-AGENT-API.md**: Add Windows platform note (host agent not yet available)
- **Langfuse README.md**: New service README (ports, env vars, volumes, troubleshooting)
- **CATALOG.md**: Add missing Langfuse entry
- **.env.example**: Document `LLAMA_CPU_LIMIT` for macOS/CPU-only mode
- **SUPPORT-MATRIX.md**: Link to AMD system-tuning guide
- **Root README.md**: Fix Apple Silicon "4B" → "9B" for 16-24GB tier

Every claim was verified against source code by an Opus-level critique pass (tier-map.sh, dream-cli, install-windows.ps1, dream.ps1, dream-host-agent.  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
