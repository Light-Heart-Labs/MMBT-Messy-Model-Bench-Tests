# PR #1056 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard-api): catalog timeout, orphaned whitelist, GPU passthrough scan, health_port

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Four scoped fixes to the dashboard-api extension paths, plus three new unit tests covering the new compose-scan rule.

- **#A — Catalog/detail health-fan-out timeout:** add a separate short timeout (5 s) for the catalog and \`extension_detail\` user-extension health probes, distinct from the existing 30 s \`_HEALTH_TIMEOUT\` used elsewhere.
- **#B — Orphaned-storage whitelist:** add \`extension-progress\` and \`config-backups\` to the system-dirs set used by \`/api/storage/orphaned\`.
- **#C — GPU passthrough scan:** reject \`deploy.resources.reservations.devices\` (Compose v2 GPU syntax) in the user-extension compose security scanner, gated so built-ins can still legitimately request it.
- **#D — User-extension \`health_port\`:** read the manifest \`health_port\` field in \`scan_user_extension_services\`, mirroring the built-in \`config.py\` pattern.

## Why
**A.** \`_HEALTH_TIMEOUT\` is a session-level 30 s default. The catalog endpoint fan-outs every user-extension health probe with that timeout. The frontend \`Extensions.jsx\` aborts \`/api/extensions/catalog\` after 8 s. A single slow user-extension health endpoint pushes the whole catalog response past the frontend abort, the page renders "Failed to load extensions catalog — Retry", every extension card vanishes, and ongoing polling drops out. \`extension_detail\` has the same fan-out shape and the same DoS surface.

**B.** \`/api/storage/orphaned\` whitelists \`{models, config, user-extensions, extensions-libra  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
