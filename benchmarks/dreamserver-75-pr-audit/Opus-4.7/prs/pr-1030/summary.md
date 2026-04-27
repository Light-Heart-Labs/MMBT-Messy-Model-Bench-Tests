# PR #1030 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(host-agent): install flow — built-in hooks, bind-mount anchor, post-up state verify

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Fix five clustered defects in the host agent's extension install flow that combined to produce silent install failures.

## Why
- Built-in extensions declaring a `post_install` hook had their hooks silently skipped — the ext_dir was hardcoded to the user-extensions directory so `_resolve_hook` never found the manifest.
- `_precreate_data_dirs` had the same hardcode, plus a prefix filter that only caught `./data/` bind-mount sources. Community extensions like label-studio (`./upload`, `./media`, `./www`), continue and sillytavern (`./config/...`) were skipped, Docker auto-created those dirs as `root:root`, and non-root containers broke on Linux.
- Relative paths in extension compose files were resolved against `INSTALL_DIR`, but Docker Compose resolves them against the compose file's directory — dirs were created in the wrong place.
- Post-`compose up -d` progress was written as "started" unconditionally on return-code zero, which Docker emits for Exited/Created/Restarting containers as well as Running. The dashboard showed green for crash-looping services.

## How
1. `_run_install` and `_precreate_data_dirs` now call `_find_ext_dir(service_id)`.
2. Prefix filter widened: any relative bind-mount source (no leading `/`, contains `/`) is now pre-created; named volumes are still skipped.
3. `dir_path` and the traversal safety check both anchor on `ext_dir`.
4. `_handle_install` polls `docker inspect --format '{{.State.Status}}|{{.State.Error}}'` for up to 15s (1s interval  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
