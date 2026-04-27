# Upstream Context

## Architecture Surfaces Used In The Audit

DreamServer's open PR queue concentrated around these upstream contracts:

- `dream-server/installers/` - platform installers and phase scripts.
- `dream-server/bin/dream-host-agent.py` - dashboard-to-host/Docker bridge for install, model activation, extension lifecycle, and native service control.
- `dream-server/scripts/resolve-compose-stack.sh` - central compose stack resolver for base, GPU, extension, mode, and user-extension overlays.
- `dream-server/dream-cli` - operator CLI, service management, config display, GPU commands, and compose flag caching.
- `dream-server/extensions/services/dashboard-api/` - FastAPI backend for setup, extensions, GPU status, settings, and host-agent calls.
- `dream-server/extensions/services/dashboard/` - React/Vite dashboard frontend.
- `dream-server/extensions/services/*/compose.yaml` and manifests - service library and extension contracts.
- `resources/dev/extensions-library/` - community/development extension source catalog.

## Key Contracts

1. **No LAN exposure by default.** Host/native services should bind loopback unless explicitly configured otherwise.
2. **Compose fragments are evaluated together.** A required interpolation in one extension can break unrelated operations if included in the merged stack.
3. **Install paths need server-side enforcement.** Catalog/UI flags are not sufficient if a direct API path can bypass them.
4. **Resolver output is shared state.** Install phases, CLI, preflight, validation, and cached `.compose-flags` must agree.
5. **GPU backend differences are first-class.** NVIDIA UUIDs, AMD indices/ROCr, Apple aggregate GPU, and CPU modes cannot be treated as one generic GPU path.

## Audit Consequences

- PRs that fixed only the visible dashboard path but not direct install/API paths were marked revise.
- PRs that changed compose syntax were tested as merged stacks where possible.
- AMD-related PRs were scored with extra risk because regressions harm a strategic partnership, not only a niche feature.
