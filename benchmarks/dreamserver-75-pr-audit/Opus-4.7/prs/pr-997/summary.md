# PR #997 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dream-cli): pre-validate 'dream shell' service + Docker daemon preflight

## Author's stated motivation

The PR body says (paraphrased):

> ## What

Three improvements to `dream shell <service>`:

1. **Pre-validate the service ID against the registry** before any Docker call, so `dream shell bogus-service` fails fast with "Unknown service" instead of emitting mismatched Docker errors.
2. **Docker daemon preflight** — distinguish "daemon down" from "container stopped" so the error message reflects the actual cause. Uses `perl -e 'alarm 3; exec "docker", "info"'` for a portable 3-second timeout (`timeout` isn't on stock macOS).
3. **Probe for `/bin/bash`** via `docker exec <c> test -x /bin/bash` before choosing the shell, so the `/bin/sh` fallback only fires on images that genuinely lack bash (instead of firing on any exec failure).

## Why

The original code printed an optimistic "Opening shell..." log, then Docker emitted "No such container" twice — once for `/bin/bash` and once for the fallback — before exiting. Misleading UX. The existing container-running check (`docker ps`) also returns non-zero when the daemon itself is down, so users whose Docker Desktop wasn't running saw "Container X is not running" and tried `dream start` (which also failed), creating a confusing loop.

`docker info` can hang for 20+ seconds when Docker Desktop is mid-boot (socket exists, daemon not yet accepting RPCs); the `perl alarm` wrapper gives a portable 3-second timeout.

## How

Two commits:

- `14c3d869` — service ID validation, container-running check, `/bin/bash` probe before fallback.
- `ca08b830` — call `sr_load` directly i  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
