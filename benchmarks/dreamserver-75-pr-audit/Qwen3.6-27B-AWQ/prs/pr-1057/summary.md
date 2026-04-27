# PR #1057 Summary

**Title:** fix(host-agent): runtime hygiene — narrow pull, surface failures, normalize bind volumes
**Author:** yasinBursali (established contributor, 63/75 PRs)
**Claimed bounty tier:** Not explicitly stated (yasinBursali PRs are typically core maintenance)

## What the PR claims to do

Seven surgical edits in `dream-server/bin/dream-host-agent.py`:

1. **Narrow `docker compose pull`** — Filter out other extensions' compose files during pull to avoid `${VAR:?}` guard failures from unrelated extensions
2. **Fix stderr head-truncation** — Change `stderr[:N]` to `stderr[-N:]` at 3 sites so the actual error (at end of stderr) is surfaced instead of the preamble
3. **Surface OSError in `_write_model_status`** — Log disk-full/permission errors instead of silently swallowing them
4. **Raise on `_recreate_llama_server` failure** — Add `raise RuntimeError` after logging docker run failure, preventing 5-minute health-check hangs
5. **HTTP 403/500 separation** — Distinguish "model not in catalog" (403) from "catalog unavailable" (500) in model download/list handlers
6. **Handle dict-form Compose volumes** — Support long-form `{type: bind, source: ..., target: ...}` volume syntax in `_precreate_data_dirs`
7. **Skip non-pre-expandable sources** — Skip `~`, `$VAR`, backtick, backslash sources in precreate logic

## Assessment

This is a high-quality, well-reasoned PR from the project's primary contributor. Each change addresses a specific, documented failure mode. The PR description is exceptionally detailed with platform impact analysis.
