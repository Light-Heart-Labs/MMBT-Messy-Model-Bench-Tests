# PR #1039 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(host-agent): retry install failure through the hook + progress path

## Author's stated motivation

The PR body says (paraphrased):

> > **DRAFT: must merge AFTER #1030.** This branch is based on `fix/host-agent-install-flow` (#1030) and depends on `_find_ext_dir` for built-in hook discovery. Promote to ready-for-review after #1030 merges.

## Summary
Clicking **Enable** on an extension whose install left `{"status":"error"}` in its progress file silently took a different path from the original install: `docker compose up` without re-running the `post_install` hook and without writing the progress file. UI stayed stuck on the old error; extensions that failed because a hook didn't write required env vars failed again on retry for the same root cause.

## How
When `_handle_extension("start")` sees an error-status progress file, it now delegates to a daemon-thread retry path that:

1. Responds **202** with `{"status": "retrying"}` immediately (matches `_handle_install`'s 202-then-poll shape).
2. Writes `{"status": "starting"}` transitionally.
3. Re-runs the `post_install` hook if declared, with the **same argv / cwd / env allowlist** as `_handle_install` (no secrets leak — PATH, HOME, SERVICE_ID, SERVICE_PORT, SERVICE_DATA_DIR, DREAM_VERSION, GPU_BACKEND, HOOK_NAME only).
4. On hook success → `docker compose up`; writes `{"status": "started"}` or `{"status": "error"}` with compose stderr.
5. On hook failure → writes `{"status": "error"}` with hook stderr; compose not called.

**Non-retry paths** (stop, start-without-error, start-with-no-progress-file) preserve the existing synchronous `docker_compose_action` b  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
