# PR #983 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> feat(resources): add p2p-gpu deploy toolkit for Vast.ai GPU instances

## Author's stated motivation

The PR body says (paraphrased):

> ### What

One-command DreamServer deployment on peer-to-peer GPU marketplaces (Vast.ai). Handles 28 known provider quirks — root user rejection, Docker socket permissions, NVIDIA/AMD toolkit setup, model bootstrapping, multi-GPU topology, reverse proxy, and SSH tunnel generation.

### Where

Everything lives in `resources/p2p-gpu/` — fully self-contained, no modifications to core DreamServer code or extension manifests.

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
