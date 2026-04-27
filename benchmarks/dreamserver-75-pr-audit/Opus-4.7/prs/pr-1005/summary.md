# PR #1005 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(macos): install-time polish — DIM constant, busybox pin, healthcheck rewrite

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Three macOS-only install-time defects, each in a distinct file.

## Why / How

### 1. `DIM` color variable missing from macOS constants
`installers/macos/lib/ui.sh:180` referenced `\${DIM}` in the final
summary banner, but the macOS `lib/constants.sh` did not define it
(the shared `installers/lib/constants.sh` defines it at line 52, but
the macOS installer does not source that file). Under `set -u` the
installer crashed at the very last line — a scary UX on an install
that otherwise succeeded. Added `DIM='\033[2;37m'` to the macOS
constants, matching the shared palette.

### 2. `busybox:latest` pinned
`installers/macos/docker-compose.macos.yml` used `busybox:latest` for
both the `replicas: 0` placeholder and the active
`llama-server-ready` sidecar. The active sidecar runs a `wget`
polling loop that depends on busybox applet semantics — `:latest` is
a reproducibility risk. Pinned both references to `busybox:1.36.1`,
matching the explicit-pin pattern used elsewhere in the compose tree.

### 3. Phase-6 healthcheck loop rewrite
The installer's own HTTP poll (`MAX_ATTEMPTS=30`, 60s total) often
emitted false `not responding after 30 attempts` warnings on cold
first installs because image pull + first-run DB migrations + Docker
Desktop container startup can exceed 60s.

Replaced with `docker inspect --format '{{.State.Health.Status}}'`
for Docker services (`dream-webui`, `dream-whisper`, `dream-n8n`)
so the container's own healthcheck drives the gate. Host-native
services (  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
