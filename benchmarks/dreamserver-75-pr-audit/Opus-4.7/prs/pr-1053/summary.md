# PR #1053 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> ci(openclaw): filesystem-write gate to detect new openclaw write paths

## Author's stated motivation

The PR body says (paraphrased):

> > **DRAFT: must merge AFTER #1035.** The workflow's mechanism is independent of named-volume vs bind-mount layout (it overrides volume layout in `docker run`), so this PR can run before #1035 lands — but the gate's *purpose* (catching upstream additions to openclaw's persistent write paths) only makes semantic sense once #1035's simplified layout is the production baseline. Promote to ready-for-review after #1035 merges; this PR has no file overlap so the rebase is trivial.

## What
Add `.github/workflows/openclaw-image-diff.yml`. When a PR touches openclaw's compose.yaml or manifest.yaml, the workflow runs the openclaw image with a host bind-mount over `/home/node/.openclaw`, exercises the entrypoint briefly, then walks the bind-mount directory and fails if any file other than the expected `openclaw.json` shows up.

## Why
Without a runtime gate, a future openclaw image bump that introduces a NEW persistent state path (e.g. `/home/node/.openclaw/sessions/`, `/home/node/.openclaw/cache.db`) would silently land in the container's ephemeral overlay and be lost on every recreate, with no CI signal until users complain.

**Why not `docker diff` (as the original issue proposed):** `docker diff` reports changes to the container's union-FS writable layer only. Writes to mounted volumes — named OR bind — are invisible to it. The originally-proposed `docker diff openclaw-test | grep "/home/node/\.openclaw/"` would have always passed (zero matches), making it a false-green CI gate. Ver  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
