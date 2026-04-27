# PR #1050 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(installer): block non-POSIX INSTALL_DIR + verify Docker Desktop sharing

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Block install on a non-POSIX-permission filesystem at `INSTALL_DIR` (security regression), and pre-verify Docker Desktop's file-sharing allowlist before any compose-up. Per-platform detection across all three installers, plus a defense-in-depth guard in the host agent.

## Why
**Bug #1 — non-POSIX filesystems silently no-op chmod/chown:** Phase 06 runs `chmod 600 "$INSTALL_DIR/.env"` to lock down secrets. On exFAT, FAT32, fuseblk (NTFS via ntfs-3g), 9p, and DrvFs the chmod is a silent no-op — the kernel returns success but the permission bits are not stored. The .env file (containing `WEBUI_SECRET`, `DASHBOARD_API_KEY`, `DREAM_AGENT_KEY`, etc.) ends up world-readable on the host. **This is a security regression**, not just an install oddity.

**Bug #2 — Docker Desktop file-sharing allowlist not pre-verified:** macOS / Windows Docker Desktop maintains an allowlist of host paths that can be bind-mounted into containers. Custom install paths (`/opt/dreamserver`, `/mnt/external`, etc.) outside the default allowlist cause `docker compose up` to fail with a cryptic OCI error (`error mounting ... to rootfs`) on every service. No diagnostic guidance is surfaced.

Both gaps existed across all three platform installers with zero detection.

## How
Per-platform filesystem-type detection at the nearest existing parent of `INSTALL_DIR`, plus a Docker Desktop bind-mount probe. Treats the non-POSIX FS types as **fatal** (refuse install with clear remediation message); host agent ski  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
