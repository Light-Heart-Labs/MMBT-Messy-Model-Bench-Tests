# Pre-PR Baseline State

This is the **state of `main`** that every PR is being compared against.
A "regression" in any verdict means: *behavior differs from what's documented
here*.

## Git baseline

| Field | Value |
|-------|-------|
| Commit | `d5154c37f2f9a4b3eb896b729d989db96ed308f0` |
| Subject | `Merge pull request #987 from Light-Heart-Labs/codex/windows-installer-llm-endpoint-fixes` |
| Date | 2026-04-23 |
| Branch | `main` |

## Repo shape (top-level, baseline)

```
.github/                    CI workflows
dream-server/               Core product
  install-core.sh           184-line orchestrator
  installers/lib/           Pure-function libraries
  installers/phases/        13 sequential install phases (01..13)
  installers/macos/         macOS variant
  installers/windows/       Windows variant (PowerShell)
  extensions/services/      19 service extensions, each a manifest+compose
  docker-compose.base.yml   Core service compose
  docker-compose.{amd,nvidia,apple}.yml  GPU overlays
  dream-cli                 Bash CLI (~45K lines)
  config/                   Backend configs, ports, hardware DB
  scripts/                  Health, model, compose-resolve, doctor, preflight
  tests/                    Shell + BATS + contract tests
  lib/                      Shared Bash utilities
installer/                  Outer wrapper installer scaffolding
install.sh / install.ps1    Top-level installer entry points
resources/                  Cookbooks, blog, frameworks, dev tools
```

## Service inventory (baseline, from ARCHITECTURE.md)

19 services across these functional areas:

| Area | Services |
|------|----------|
| Inference | llama-server (CUDA / ROCm / Vulkan / Metal / CPU), litellm |
| Chat & UI | open-webui, dashboard, dashboard-api |
| Search | searxng, perplexica |
| Agents | openclaw, ape, n8n |
| RAG | qdrant, embeddings (TEI) |
| Voice | whisper, tts (Kokoro) |
| Media | comfyui |
| Privacy/Obs | privacy-shield, token-spy, langfuse |
| Dev | opencode |

All services bind to `127.0.0.1` (per security policy at baseline; verified
against `SECURITY_AUDIT.md` H3 remediation).

## Test commands (baseline)

These run from `dream-server/`:

```bash
make lint        # bash -n + Python compile check
make test        # tier-map + contracts + preflight fixtures
make smoke       # platform smoke tests
make simulate    # installer simulation harness
make gate        # lint + test + smoke + simulate
make doctor      # diagnostics
```

## Baseline gotchas observed during audit

- Pre-existing static SearXNG secret_key in repo (SECURITY_AUDIT.md H1).
  PRs that touch `config/searxng/settings.yml` should be evaluated in light of
  this — replacing the secret without breaking existing installs is the right move.
- Pre-existing committed LiveKit credentials in `resources/frameworks/voice-agent/`
  (SECURITY_AUDIT.md C1). Out of scope for individual PRs but explains why
  voice-agent–touching PRs may have an unrelated rotation pending.
- `eval "$env_out"` pattern in `installers/lib/detection.sh` (SECURITY_AUDIT.md
  H2) — any PR that adds new `eval` of script output is a regression flag.

## Environments available for testing

| Environment | Available? | Notes |
|-------------|-----------|-------|
| Windows 11 + Git Bash (MSYS) | yes (host) | Used for PowerShell installer review |
| Linux container via Docker Desktop | yes | Used for installer / shell tests |
| Linux + NVIDIA GPU | partial | Workstation has GPUs but Docker GPU passthrough on Windows is via WSL2 |
| macOS (Apple Silicon) | **no** | Mac-specific paths reviewed by inspection only |
| AMD Strix Halo / ROCm hardware | **no** | AMD-specific paths reviewed by inspection only |
| Vast.ai / cloud GPUs | not used | Would cost money; skipped |

The "tested on" line in each PR's `tests/` directory is explicit about which
of these the PR was run against.
