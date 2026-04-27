# PR #1016 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-cli): Apple GPU output polish + compose wrapper SIGINT/zero-match

## Author's stated motivation

The PR body says (paraphrased):

> ## ⚠️ Draft — depends on #999 AND #1001 merging first

All four fixes live in code introduced by unmerged upstream PRs:
- **#401, #402** target the Apple GPU_BACKEND branches added by #999 (`fix/dream-cli-apple-silicon-coverage`)
- **#405, #407** target `_compose_run_with_summary` added by #1001 (`fix/dream-cli-compose-summary-wrapper`)

Once #999 and #1001 both merge, I'll rebase and the PR diff will reduce to just the delta shown below.

## What
Four small polish fixes on top of #999 + #1001:

- **#401** — `cmd_status_json` Apple branch was emitting `gpu_cores` as a string via `jq --arg`. Switch to `--argjson` with integer-or-null detection: numeric values become JSON integers; the fallback literal `"?"` becomes JSON `null`.
- **#402** — `dream gpu status` header hardcoded `"(${gpu_count} GPUs)"` derived from `nvidia-smi --list-gpus`. On Apple Silicon this produced `"(0 GPUs)"` despite the Apple branch below showing valid GPU info. Branch on `GPU_BACKEND=apple` to show `"(1 integrated GPU)"` instead.
- **#405** — `_compose_run_with_summary` mktemp'd a compose log but had no `trap` to clean up on SIGINT/SIGTERM. Ctrl-C during compose ops leaked `/tmp/tmp.*` files. Add `trap 'rm -f "$_compose_log"' INT TERM` after mktemp and `trap - INT TERM` before each return.
- **#407** — The error surface pipeline `grep | sed | head -20 || warn` never triggered the warn fallback when `grep` found zero matches, because `head -20` exits 0 on empty input (the pipeline exit was 0, not 1). Use  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
