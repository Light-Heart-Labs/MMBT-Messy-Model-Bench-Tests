# PR #1045 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard-api,host-agent): route extension config sync through host agent

## Author's stated motivation

The PR body says (paraphrased):

> ## Summary

`_sync_extension_config` in `routers/extensions.py` calls `shutil.copytree` to copy `<ext_dir>/config/*` into `INSTALL_DIR/config/`. The dashboard-api container has `/dream-server/config` bind-mounted **read-only** (`docker-compose.base.yml:176`, present since v2.0.0), so the copy fails:

```
OSError: [Errno 30] Read-only file system: '/dream-server/config/<svc>'
```

The helper was added later, in commit `4dbabc53` (\"fix(extensions): sync config/ subdir on install\"), without coordinating with the read-only mount. Any user-installed extension that ships a `config/<id>/` subdirectory has been silently broken on install since that change. In the current community library this affects `continue` and `sillytavern`. Built-ins are unaffected because their configs are pre-created by the installer at phase 06.

This fix follows the established pattern (see `_handle_extension_compose_toggle` / `_call_agent_compose_rename`): the dashboard-api delegates host-side mutations to the host agent, which runs on the writable host filesystem.

## What this changes

**Host agent** — new `POST /v1/extension/sync_config`:
- Bearer auth (`check_auth`), JSON body `{\"service_id\": \"...\"}`, validated against `SERVICE_ID_RE`
- Resolves under `USER_EXTENSIONS_DIR / sid` only — built-ins return a 200 no-op (their bootstrap is installer-managed; resyncing risks overwriting user-modified files)
- If `<ext>/config/` is absent, returns 200 no-op
- **Rejects all symlinks** anywhere in the con  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
