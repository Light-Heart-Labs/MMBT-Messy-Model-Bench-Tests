# PR #1042 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> feat(support): add redacted diagnostics bundle generator

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary

This adds a standalone support bundle generator for DreamServer.

The new `scripts/dream-support-bundle.sh` command creates a redacted `.tar.gz` bundle under `artifacts/support/` so users can share one consistent diagnostics package when installs, Docker, GPU detection, extension startup, or runtime health go wrong.

## What changed

- added `scripts/dream-support-bundle.sh`
- added `tests/test-support-bundle.sh`
- added `docs/SUPPORT-BUNDLE.md`

The bundle collects:
- Dream Doctor output when available
- extension audit JSON
- compose resolution and validation output
- Docker version/info/container summary when Docker is available
- short DreamServer container log tails
- platform, git, disk, memory, port, manifest, env schema, and redacted env details

It is best-effort by design:
- missing Docker does not fail the whole bundle
- failing diagnostic subcommands are recorded in the manifest instead of aborting the run
- raw `.env` is never included

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
