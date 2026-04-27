# Upstream Context

The DreamServer architecture facts that shape PR verdicts. Pulled from
`ARCHITECTURE.md`, `CLAUDE.md`, and `SECURITY_AUDIT.md` at baseline
`d5154c37f2f9a4b3eb896b729d989db96ed308f0`. If a PR touches anything in this
file, the verdict cites the relevant line here.

## 1. The two-layer split

The repo has an outer wrapper and a core product:

- **Root** — `install.sh`, `install.ps1`, `.github/workflows/`, `resources/` (cookbooks, blog, frameworks)
- **`dream-server/`** — everything that gets deployed

PRs that touch root-level paths (especially CI and `resources/`) have a
fundamentally different blast radius than PRs that touch `dream-server/`. Root
changes mostly affect contributors and the marketing surface; `dream-server/`
changes affect every install.

## 2. The installer pipeline

`install.sh` → `install-core.sh` → sources `installers/lib/*.sh` (pure) →
sources `installers/phases/01..13.sh` (imperative) sequentially:

| Phase | Purpose | High-risk because... |
|-------|---------|---------------------|
| 01 Preflight | Root/OS/tools, existing-install detect | First gate; failure here = no install |
| 02 Detection | GPU detection, tier assign, compose-select | Drives every downstream decision |
| 03 Features | Interactive feature menu | UX surface; menu logic regressions are visible |
| 04 Requirements | RAM/disk/GPU/port checks | Gates install; false negatives block users |
| 05 Docker | Docker, Compose, NVIDIA toolkit install | Touches package manager state |
| 06 Directories | Dir creation, source copy, `.env` gen | First write-to-disk phase |
| 07 DevTools | Claude Code, Codex, OpenCode CLIs | Network-heavy |
| 08 Images | Docker image pulls | Bandwidth-heavy |
| 09 Offline | Air-gap configuration | Edge-case path; thinly covered |
| 10 AMD Tuning | sysctl, modprobe, GRUB, tuned | **Privileged** OS state changes |
| 11 Services | GGUF download, models.ini, stack launch | First time the stack runs |
| 12 Health | Service health, STT pre-download | Final correctness gate |
| 13 Summary | URLs, shortcuts, summary JSON | UX only |

**Implication for verdicts:** A PR that adds a check in phase 04 (requirements)
is generally safer than one that mutates phase 05 (Docker install) or 10 (AMD
tuning). Phase 10 mutates host state in ways that are hard to roll back.

## 3. The lib/phases purity boundary

`installers/lib/` is the **pure functional core**. `installers/phases/` is the
**imperative shell**. PRs that put I/O or side-effects into a `lib/` file violate
this; PRs that put pure logic into a phase file are tolerable but wasteful. This
is called out as a design principle in `CLAUDE.md`.

When reviewing, watch for:
- New `eval`, `read -p`, `docker`, `curl`, file writes inside `installers/lib/*.sh` → architectural regression
- Conversely, refactors that move pure helpers from phases into lib are *positive* signals

## 4. The extension system

Every service is an extension under `extensions/services/<id>/`:

```
extensions/services/<id>/
  manifest.yaml      # Service contract (id, port, health, GPU backends, deps, features)
  compose.yaml       # Optional; core services live in docker-compose.base.yml
  compose.{nvidia,amd}.yaml  # GPU overlays
  Dockerfile         # If custom image
```

Manifest schema: `extensions/schema/service-manifest.v1.json`. The resolver
(`scripts/resolve-compose-stack.sh`) discovers enabled extensions and merges
their compose files with the base + GPU overlay.

**Implication for verdicts:** PRs that add new extensions but skip a manifest
field, or break the schema, will fail the resolver silently in some paths.
Verdict reviewers check that any PR adding/changing a `manifest.yaml`
keeps the schema valid.

## 5. The compose layering model

```
docker-compose.base.yml
  + docker-compose.{nvidia|amd|apple|cpu}.yml   (GPU overlay)
  + extensions/services/<id>/compose.yaml ...   (each enabled extension)
  + extensions/services/<id>/compose.<gpu>.yaml ... (GPU-specific extension overlays)
```

Composed at runtime by `scripts/resolve-compose-stack.sh`. Order matters
(later overrides earlier).

**Implication for verdicts:** PRs that change the resolver order, or add a
compose file outside this canonical layering, can break specific platforms
silently.

## 6. Port and binding policy

**Every service binds to `127.0.0.1` by default.** Canonical ports in
`config/ports.json`. `0.0.0.0` is a **security regression** unless the PR
explicitly justifies it.

`SECURITY_AUDIT.md` H3 documents that OpenClaw was previously bound to
`0.0.0.0` with `dangerouslyDisableDeviceAuth: true` — this was partially fixed
in PR #67. PR #988 in the open set is doing the same fix for `llama-server`
and the host agent; verdicts on PR #988 and any PR that touches port bindings
must respect the loopback policy.

## 7. The `BIND_ADDRESS` convention

Some PRs (e.g. #1027, #1044) use `${BIND_ADDRESS}` or `${VAR:-127.0.0.1}` in
compose port mappings. This is the right pattern: lets the binding be lifted
to `0.0.0.0` via env var when explicitly requested, defaults to safe.
Verdicts approve this pattern.

## 8. Coding-style hard rules (from `CLAUDE.md`)

These are not preferences; they are documented rules. PRs that violate them
should be rejected for **fit** unless the rule violation is justified.

| Rule | Implication for verdicts |
|------|--------------------------|
| **No broad/silent catches.** No `except Exception: pass`, no `2>/dev/null`, no `\|\| true` in bash. | Any PR adding these patterns gets a **REJECT — fit** or **REVISE — small** unless the catch is narrowly scoped and meaningful. |
| **No retry/backoff loops.** | PRs that add retries get scrutinized hard. Health-check `start_period` extension is a different category — that's not retry, that's giving slow startup more headroom. |
| **No fallback chains.** | PRs with cascading try/except get rejected. |
| **Bash uses `set -euo pipefail` everywhere.** | PRs that turn off pipefail or add unguarded `\|\| true` are regressions. |
| **Tests should let assertions fail visibly.** | PRs that catch in tests to avoid failure are rejected. |
| **Internal functions: let exceptions propagate.** | Narrow exceptions only at I/O boundaries. |

Notable nuance: `start_period: 600s` is a healthcheck tuning, not retry logic.
Some PRs (e.g. #1028 on embeddings) extend healthcheck windows; those are fine.

## 9. Cross-platform scope

Three OS targets, four GPU backends:

| OS / Backend | NVIDIA | AMD | Apple Silicon | Intel Arc | CPU |
|--------------|:------:|:---:|:-------------:|:---------:|:---:|
| Linux | ✓ | ✓ | — | exp | ✓ |
| Windows | ✓ (WSL2) | ✓ (Lemonade) | — | — | ✓ |
| macOS | — | — | ✓ (Metal) | — | ✓ |

PRs that touch one platform must not regress others. Yasin's PRs frequently
note Apple Silicon; Y/y-coffee-dev's #750 is multi-GPU AMD. The matrix-smoke CI
covers Ubuntu, Debian, Fedora, Arch, openSUSE; macOS and Windows do not have
matrix-smoke equivalents and rely on inspection / dev-machine testing.

## 10. CI gate (what runs before merge)

| Workflow | What gates | Failure means |
|----------|-----------|---------------|
| `lint-shell.yml` | `shellcheck` on all `.sh` | New `SC2086`, `SC2168`, etc. blocks merge |
| `lint-python.yml` | ruff/black | Style regression blocks merge |
| `type-check-python.yml` | mypy | Type regression blocks merge |
| `dashboard.yml` | Dashboard build + lint | UI regression blocks merge |
| `test-linux.yml` | Integration suite | Functional regression blocks merge |
| `matrix-smoke.yml` | 6-distro smoke | Per-distro regression blocks merge |
| `validate-compose.yml` | Compose validity | Bad compose blocks merge |
| `validate-env.yml` | `.env.schema.json` validity | Bad env schema blocks merge |
| `secret-scan.yml` | gitleaks | New committed secret blocks merge |
| `lint-powershell.yml` | PSScriptAnalyzer on `.ps1` | Windows regression blocks merge |

**Implication for verdicts:** When a PR's CI is **green**, the verdict can
trust shellcheck, type-check, etc. The auditor's job is to find what CI
*doesn't* catch — design issues, cross-PR conflicts, and regressions in
behavior that the test suite doesn't exercise.

## 11. Active partnerships and constraints

- **AMD developer program partnership.** AMD GPU paths must not regress.
  PRs touching AMD-specific code (Lemonade, ROCm, AMD overlays, AMD tuning
  in phase 10, Strix Halo configs) are flagged in `executive-summary.md`.
- **400+ stars, bounty-incentivized contributors.** Bounty PRs (Small/$40,
  Medium/$150, Large/$400) have different signal than core-contributor PRs.
  Verdicts call out tier mismatch (a "Large" that only touches three lines).

## 12. Known security-audit context (latentcollapse, 2026-03-08)

Pre-existing audit findings that should inform verdicts on related PRs:

| Finding | Severity | Open-PR relevance |
|---------|----------|---------|
| C1 — committed LiveKit credentials | Critical | Out of scope for any open PR; rotation is a separate workstream |
| H1 — static SearXNG secret_key | High | No open PR addresses this; flagged for backlog |
| H2 — `eval $env_out` in detection | High | Any PR adding new `eval` is a regression flag |
| H3 — OpenClaw `dangerouslyDisableDeviceAuth` + `0.0.0.0` | High | PR #67 addressed; **PR #988** in this set extends the loopback fix to llama-server + host agent |
| M1 — `f"ALTER TABLE"` in token-spy | Medium | Any PR touching `token-spy/db.py` should re-evaluate this |
| M2 — dashboard / token-spy run as root | Medium | No open PR addresses |
| M5 — `local` outside function | Medium | Already addressed in PR #72 (closed) |

## 13. Rapid-fire principles for verdict authors

When in doubt, defer to these:

1. **Loopback by default** — any new port binding must default to `127.0.0.1` or use `${BIND_ADDRESS:-127.0.0.1}`.
2. **Pure libs, imperative phases** — keep `installers/lib/` side-effect-free.
3. **Schema-driven** — extending behavior should mean editing a manifest or a JSON config, not a switch statement.
4. **Cross-platform respect** — no Linux-only feature that breaks Mac/Windows silently. Any platform-conditional logic uses the established detection layer.
5. **Let it crash** — a PR that adds `try: ... except: pass` is almost never right.
6. **Backwards-compatible env** — existing installs read `.env` via `safe-env`; new env vars need defaults that don't break first-time-readers.
