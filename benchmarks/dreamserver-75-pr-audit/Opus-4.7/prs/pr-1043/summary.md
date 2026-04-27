# PR #1043 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(installer): custom menu's 'n' answers were not actually disabling services

## Author's stated motivation

The PR body says (paraphrased):

> Fixes two compounding bugs caused users in Custom mode to get almost every optional service installed regardless of their answers:

1. The prompt logic used '[[ $REPLY =~ ^[Nn]$ ]] || ENABLE_X=true', which only SET flags to true and never to false. Since install-core defaults were already true (VOICE/WORKFLOWS/RAG/OPENCLAW/COMFYUI/ DREAMFORGE), pressing 'n' was a no-op. Replaced with explicit if/else branches that set the flag from the user's answer.

2. Only ComfyUI, DreamForge, and Langfuse had the compose.yaml → .disabled rename logic. For whisper, tts, n8n, qdrant, openclaw the ENABLE_* flag only gated cosmetic things (image pre-pull, health checks, summary URLs) — the compose file was always picked up by resolve-compose-stack.sh, so the service started anyway. Refactored the three existing rename blocks into a reusable helper and extended coverage to voice/workflows/rag/openclaw.

Also added the missing CLI equivalents --no-voice, --no-workflows, --no-rag, --no-openclaw so non-interactive installs get the same opt-out coverage as the Custom menu.

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
