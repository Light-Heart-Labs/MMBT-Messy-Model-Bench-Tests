# PR #1027 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(extensions): bind community extension ports via ${BIND_ADDRESS}

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Replace hardcoded `127.0.0.1:` port bindings in 29 community extension compose files with `${BIND_ADDRESS:-127.0.0.1}:`, matching the pattern established for core services. Wire a new regression test into `make test`.

## Why
Community extensions in `resources/dev/extensions-library/services/` hardcoded `127.0.0.1:` on every `ports:` entry. When users opted into LAN exposure via `--lan`, the dashboard network-mode toggle, or `BIND_ADDRESS=0.0.0.0` in `.env`, only core services responded to the setting. All 29 community extensions remained loopback-only, silently ignoring user intent.

## How
- Rewrote 35 port-binding lines across 29 compose files:
  `"127.0.0.1:${EXT_PORT:-NNNN}:NNNN"` → `"${BIND_ADDRESS:-127.0.0.1}:${EXT_PORT:-NNNN}:NNNN"`
- Healthcheck `test:` URLs (container-internal loopback) intentionally preserved — they are not host-exposed bindings.
- Added `dream-server/tests/test-bind-address-sweep.sh`: greps all community extension compose files for bare `127.0.0.1:` port-line entries (bidirectional-verified: passes clean, fails clearly on revert).
- Wired the new test into `dream-server/Makefile` `test:` target; inherited by `gate:` via `gate: lint test bats smoke simulate`.

## Testing
- **Automated:** YAML parse validated; `docker compose -f <sample> config` verified port-string substitution is correct; regression test (`test-bind-address-sweep.sh`) passes clean and fails with a clear message when a file is reverted; `make -n test` confirms the new test   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
