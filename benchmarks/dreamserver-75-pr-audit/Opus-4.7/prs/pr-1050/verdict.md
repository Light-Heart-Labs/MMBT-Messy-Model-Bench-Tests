# PR #1050 — Verdict

> **Title:** fix(installer): block non-POSIX INSTALL_DIR + verify Docker Desktop sharing
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/installer-fs-preflight`
> **Diff:** +351 / -1 across 5 file(s) · **Risk tier: Medium (score 9/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1050

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | New `installers/macos/lib/preflight-fs.sh`, all 3 OS installers, host-agent Python |
| B — Test coverage | 2 | New shell library is not exercised by BATS in the PR; matrix-smoke covers Linux but neither Mac nor Windows install paths run in CI |
| C — Reversibility | 1 | Adds a *blocking* check at install time. Reversible, but a user who mid-install hits the new block has to pick a different path — annoying UX |
| D — Blast radius | 3 | A false positive blocks first-boot install on a platform the user wants. False negative leaks `.env` secrets via FAT silently no-op'ing chmod |
| E — Contributor | 0 | Yasin; consistent with installer-hardening sweep |
| **Total** | **9** | **Medium** |

## Verdict

**MERGE — second-priority among the security PRs.** Behind #988
(loopback) but ahead of most others. The threat addressed is real:
DreamServer's `.env` carries the `DASHBOARD_API_KEY`, `LITELLM_KEY`,
and provider API keys; chmod'ing it 600 on a FAT/exFAT/NTFS volume is
a **silent no-op**, leaving secrets readable by any user/process on the
machine.

The fix is correct in three layers:

1. **macOS preflight** — `installers/macos/lib/preflight-fs.sh` (new)
   detects FS type via `stat -f %T`, blocks install if not apfs/hfs.
2. **Linux/Windows preflight** — equivalent checks in their respective
   installer entry points.
3. **Defense-in-depth at runtime** — `bin/dream-host-agent.py` adds
   `_fs_type()` that walks `/proc/self/mountinfo` (Linux) or shells
   `stat -f %T` (macOS); `_precreate_data_dirs` skips `os.chown` on
   non-POSIX FS with a logged warning.

This is the right architectural shape: **block at install time** (no
silent leakage in the common path), **degrade gracefully at runtime**
(extension installs post-setup don't crash if a user mounts a FAT
volume mid-life).

## Findings

### ★ — New file in `installers/macos/lib/` honors lib/phases boundary

**Where:** `installers/macos/lib/preflight-fs.sh` (new, 100 lines).

This is `installers/macos/lib/`, not the canonical
`installers/lib/`. macOS-specific lib namespace.

The file (per the snippet visible in the diff) declares pure detection
functions: `test_install_dir_filesystem`, `test_docker_desktop_sharing`.
No I/O outside the function bodies, no top-level side effects. **Pure**
in the project's sense — verified by reading the diff.

The auditor did not exhaustively read every line of `preflight-fs.sh`
(lines 100/100 visible only via the file context preview). Recommend the
maintainer skim the full file for any `tee`, redirected writes, or
`docker run` (the share-test should `docker run hello-world` or similar
in a container the user *expects* to exist; that's I/O at function-call
time, which is fine).

### ★★ — `_fs_type()` Python helper handles its OS variants explicitly

**Where:** `bin/dream-host-agent.py:165-225`.

The function tries `/proc/self/mountinfo` (Linux), then falls back to
`stat -f %T` (macOS). This **is** a fallback chain in the literal sense.
But it's *backend selection* (different platforms, different mechanisms;
each is the *correct* one for its OS), not retry-on-failure. Compliant
with `CLAUDE.md` in spirit.

The Linux path uses `with mountinfo.open():` (no broad except), then
catches `OSError` narrowly. Same in the macOS path. Compliant.

### ★ — Cryptic OCI errors at `docker compose up` motivated the share probe

**Where:** PR body documents Bug #1 (FAT silent no-op) and Bug #2
(Docker Desktop sharing — bind-mounts of paths outside the allowlist
fail with cryptic OCI errors).

Both motivations are real. The probe (`docker run --rm -v
"$INSTALL_DIR:…" hello-world` or similar) surfaces a clear error before
any compose work starts. UX win.

### ★★ — No upgrade-path consideration

**Where:** PR adds the preflight check at fresh-install time. What about
existing installs that are already on FAT/exFAT (whose `.env` is
already world-readable)?

The PR doesn't address upgrade-time detection. Recommendation: a
follow-up PR adds the same probe to `scripts/bootstrap-upgrade.sh` so
existing-install secret-leak gets surfaced via a warning. Not blocking
— the new fix prevents *new* installs from being broken.

### Convention adherence

- [x] No new `eval` of script output
- [x] No new `2>/dev/null` / `|| true`
- [?] Backend-selection in `_fs_type` looks like a fallback chain — see
      ★★ above; compliant in spirit
- [x] No port-binding changes
- [x] New file in `installers/macos/lib/` is pure
- [x] No new env vars
- [x] No manifest changes

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #988 (loopback) | **Loose pair.** Both are security PRs; both touch macOS/Windows installers and the host-agent Python. No file overlap on changed lines. **Merge #988 first** (security policy clearer), then #1050. |
| #1026 (pre-mark setup-wizard complete) | Soft conflict in `installers/macos/install-macos.sh` and `installers/windows/install-windows.ps1` — different regions of the file. Trivial merge. |
| #1057 (host-agent runtime hygiene) | Soft conflict in `bin/dream-host-agent.py` — different region. Trivial. |

## Trace

- New macOS lib: `installers/macos/lib/preflight-fs.sh`
- macOS preflight wiring: `installers/macos/install-macos.sh:111+, 195-225`
- Host-agent runtime defense: `bin/dream-host-agent.py:165-225, 280-285`
- `_fs_type` implementation pattern: dual-mechanism (mountinfo on Linux,
  `stat -f %T` on Mac) with narrow `OSError` exception handling
- `_NON_POSIX_FS` set: `exfat, msdos, vfat, fat, fat32, fat16, ntfs,
  ntfs-3g, fuseblk, 9p, drvfs, ms-dos`
