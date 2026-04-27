# Upstream Context: DreamServer Architecture

## Core Architecture

DreamServer is a self-hosted AI platform that orchestrates 19+ microservices via Docker Compose across four GPU backends (NVIDIA, AMD, Apple Silicon, Intel Arc) and CPU-only fallback.

### Layered Compose Model

```
docker-compose.base.yml          # Core services (llama-server, open-webui, dashboard, etc.)
docker-compose.{amd,nvidia,apple,intel}.yml  # GPU-specific overlays
docker-compose.override.yml      # User overrides (if present)
extensions/services/*/compose.yaml  # Extension fragments
```

The resolver (`scripts/resolve-compose-stack.sh`) discovers and assembles the correct compose stack based on:
1. GPU backend detection (amd/nvidia/apple/intel/none)
2. Dream mode (local/hybrid/lemonade)
3. Enabled extensions (from manifests)
4. GPU count (multi-GPU overlay)

### Key Components

| Component | Path | Role |
|-----------|------|------|
| Host Agent | `dream-server/bin/dream-host-agent.py` | Dispatcher between dashboard API and Docker |
| Dashboard API | `dream-server/extensions/services/dashboard-api/` | FastAPI backend for the control panel |
| Dashboard UI | `dream-server/extensions/services/dashboard/` | SvelteKit frontend |
| CLI | `dream-server/dream-cli` | Bash CLI for lifecycle management |
| Installer | `dream-server/installers/` | Platform-specific installers (Linux/macOS/Windows) |
| Extensions Library | `resources/dev/extensions-library/` | Curated extension services |

### GPU Backends

| Backend | Overlay | Acceleration |
|---------|---------|-------------|
| NVIDIA | `docker-compose.nvidia.yml` | CUDA |
| AMD | `docker-compose.amd.yml` | ROCm |
| Apple Silicon | `docker-compose.apple.yml` | Metal (native llama-server) |
| Intel Arc | `docker-compose.intel.yml` | Level Zero |
| CPU | None | CPU-only fallback |

### macOS特殊性

On macOS, llama-server runs natively on the host (not in Docker). The Docker service has `replicas: 0`. A `llama-server-ready` sidecar polls the native llama-server via `host.docker.internal`. This means:
- `depends_on: llama-server: service_healthy` would hang forever on macOS
- Extensions that depend on llama-server must use the `llama-server-ready` sidecar instead
- PR #1004 addresses this by skipping `compose.local.yaml` on Apple Silicon

### Security Model

- Host agent binds to loopback (127.0.0.1) by default on macOS/Windows
- Linux auto-detects Docker bridge gateway IP (falls back to 127.0.0.1 post-#988)
- API keys are auto-generated during install
- Secret masking in `dream config show` and dashboard API

### Extensions System

Each extension has:
- `manifest.yaml` — service metadata (schema_version, service config, gpu_backends)
- `compose.yaml` — Docker Compose fragment
- Optional GPU overlays (`compose.amd.yaml`, `compose.nvidia.yaml`, etc.)
- Optional setup hooks (`hooks/post_install.sh`)

The resolver scans `extensions/services/` and `data/user-extensions/` for enabled extensions.
