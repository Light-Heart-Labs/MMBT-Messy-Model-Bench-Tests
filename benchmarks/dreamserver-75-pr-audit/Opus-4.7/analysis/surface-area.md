# Surface Area

What each open PR touches, classified by subsystem. Generated from
`analysis/scripts/cluster_prs.py` against `analysis/cluster_summary.json`.

The classifier walks files in priority order — `installer-windows` matches
before `docs` so a PR with one `.ps1` and one `.md` lands as
`installer-windows`. Order documented in `cluster_prs.py`.

## Subsystem distribution (primary subsystem per PR)

| Count | Subsystem | What lives there |
|------:|-----------|------------------|
| 12 | `dashboard-api` | FastAPI backend (`extensions/services/dashboard-api/`) — routers, host-agent integration, GPU detection, extension lifecycle |
| 10 | `dream-cli` | The 45K-line Bash CLI (`dream-server/dream-cli`) |
| 5 | `env-schema` | `.env.schema.json`, `.env.example` |
| 5 | `docs` | Markdown documentation |
| 4 | `installer-macos` | macOS installer scripts |
| 4 | `scripts-shell` | `scripts/` operational shell utilities |
| 4 | `tests` | BATS, contract, integration tests |
| 3 | `dashboard-ui` | React dashboard frontend |
| 3 | `host-agent` | `bin/dream-host-agent.py` |
| 3 | `resources` | Top-level `resources/` (cookbooks, frameworks, p2p) |
| 3 | `ci` | GitHub Actions workflows |
| 2 | `compose-resolver` | `scripts/resolve-compose-stack.sh` and related |
| 2 | `installer-windows` | PowerShell installer |
| 2 | `installer-core` | `installers/lib/`, `installers/phases/` |
| 2 | `jupyter` | Jupyter extension |
| 2 | `langfuse` | Langfuse extension |
| 1 each | `compose-base`, `compose-extensions`, `continue`, `milvus`, `openclaw`, `perplexica`, `piper-audio`, `searxng` | Extension-specific |
| 1 | `manifests-extensions` | Extension `manifest.yaml` files |
| 1 | `whisper-stt` | Whisper / STT |

## Hot-spot files (touched by 2+ PRs)

This is the dependency-graph seed. If two PRs touch the same hot-spot file,
they conflict at minimum textually; whether they *semantically* conflict is
in `analysis/dependency-graph.md`.

| Touches | File | PRs |
|--------:|------|-----|
| 15 | `dream-server/dream-cli` | #750 #993 #994 #997 #998 #999 #1000 #1002 #1006 #1007 #1008 #1011 #1016 #1018 #1020 |
| 10 | `dream-server/bin/dream-host-agent.py` | #988 #1017 #1021 #1030 #1035 #1039 #1040 #1045 #1050 #1057 |
| 8 | `dream-server/extensions/services/dashboard-api/routers/extensions.py` | #1022 #1037 #1038 #1039 #1044 #1045 #1054 #1056 |
| 6 | `dream-server/extensions/services/dashboard/src/pages/Extensions.jsx` | #1003 #1015 #1018 #1019 #1037 #1038 |
| 6 | `dream-server/.env.schema.json` | #750 #988 #994 #1010 #1017 #1018 |
| 6 | `dream-server/.env.example` | #750 #973 #988 #992 #1013 #1017 |
| 6 | `dashboard-api/tests/test_host_agent.py` | #1021 #1030 #1035 #1039 #1040 #1045 |
| 6 | `dashboard-api/tests/test_extensions.py` | #1022 #1037 #1038 #1044 #1045 #1056 |
| 5 | `scripts/dream-test-functional.sh` | #1003 #1011 #1015 #1018 #1019 |
| 5 | `installers/macos/install-macos.sh` | #988 #1005 #1017 #1026 #1050 |
| 5 | `installers/windows/install-windows.ps1` | #988 #996 #1012 #1017 #1026 |
| 4 | `dashboard-api/routers/setup.py` | #1003 #1015 #1018 #1019 |
| 4 | `dashboard/src/components/SetupWizard.jsx` | #1003 #1015 #1018 #1019 |
| 4 | `dashboard/src/components/TemplatePicker.jsx` | #1003 #1015 #1018 #1019 |
| 4 | `dashboard/src/lib/templates.js` | #1003 #1015 #1018 #1019 |

55 distinct files are touched by 2+ PRs. Full list lives in
`analysis/file_overlaps.json`.

## What this tells the maintainer

- **`dream-cli` (15 PRs) is the single biggest convergence point.** Every
  Yasin-authored fix to the CLI shares a file with 14 other PRs. Merging in
  any order will produce conflicts to resolve. The right move is either
  (a) a stacked-PR sequence with explicit ordering or (b) a single bundled
  CLI-cleanup PR. See `decisions/0002-stack-or-bundle.md`.

- **`dream-host-agent.py` (10 PRs)** — same problem, more concentrated. The
  host-agent rewrites in #988 (security loopback), #1021 (sidecar start),
  #1030 (install flow), #1039 (retry), #1045 (config-sync route), #1050
  (POSIX/sharing preflight), #1057 (runtime hygiene) all converge. They have
  a clear logical order — security → install flow → runtime polish — but
  none of them name that order explicitly.

- **Setup-wizard cluster (#1003 #1015 #1018 #1019)** — four PRs all touch
  `Extensions.jsx`, `SetupWizard.jsx`, `TemplatePicker.jsx`, `templates.js`,
  `setup.py`, and `dream-test-functional.sh`. These four PRs are essentially
  one work product split across four PRs.

- **`.env.schema.json` and `.env.example` (6 each, mostly different sets)**
  — env additions are easy to merge if disjoint (different keys), but PRs
  #750 and #988 both touch the schema; need to verify keys don't collide.

## Cross-platform exposure

PRs that touch all three platforms simultaneously (root install + macOS +
Windows installer entry points): #988 (security loopback), #1017 (Linux
host-agent docs), #1026 (pre-mark setup wizard complete on success).

A change to one of those is a change to all three release lines. Verdicts
on these PRs evaluate per-platform.
