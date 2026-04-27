# PR #1021 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(host-agent): start extension sidecars during install

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Remove `--no-deps` from the `docker compose up -d` call inside `_handle_install()` so that extension sidecar services and cross-extension `depends_on` targets start correctly when an extension is installed.

## Why
`_handle_install()` called `docker compose up -d --no-deps <service>`, which tells Compose to bring up only the named service and skip everything it depends on. Extensions that declare private sidecar containers in their own compose fragment (e.g. a paperless extension shipping its own postgres and redis) had those sidecars silently ignored. Cross-extension `depends_on` relationships (e.g. perplexica → searxng) were also skipped, leaving services in a broken state after install.

## How
One-character change: drop `"--no-deps"` from the `subprocess.run` argv in `_handle_install()` (line 1151 of `bin/dream-host-agent.py`). `docker_compose_recreate()` — used for core-service force-recreate after a model swap — retains `--no-deps` intentionally; that call site is unchanged.

## Testing
- 40/40 tests pass in `dashboard-api/tests/test_host_agent.py`
- New `TestInstallStartCommandNoDeps` regression test uses `inspect.getsource` (file's existing pattern) to lock the argv shape for both paths:
  - `test_install_up_command_does_not_pass_no_deps` — asserts `--no-deps` absent from `_handle_install`
  - `test_docker_compose_recreate_still_uses_no_deps` — asserts `--no-deps` present in `docker_compose_recreate`
- No behaviour change for single-service extensions (they ha  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
