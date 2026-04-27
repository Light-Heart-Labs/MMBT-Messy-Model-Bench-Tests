# DreamServer Architecture Context for PR #1057

## Overview

PR #1057 modifies `dream-server/bin/dream-host-agent.py`, the host agent responsible for installing, starting, and managing extensions (Docker Compose-based services) on the DreamServer host.

## Key Components

### 1. Host Agent (`dream-host-agent.py`)

- **Role**: HTTP server that receives extension installation requests from the main DreamServer container.
- **Entry Point**: `main()` starts a `ThreadedHTTPServer` on port 8000.
- **Request Handler**: `AgentHandler` processes POST requests for:
  - `install`: Install and start an extension
  - `uninstall`: Stop and remove an extension
  - `status`: Report installation progress
  - `models`: List available models
  - `activate`: Activate a model for inference

### 2. Extension Installation Flow

The `install` endpoint follows this sequence:

1. **Precreate Data Dirs**: Create host directories for bind mounts.
2. **Pull**: Pull Docker images (best-effort; cached images allow proceeding).
3. **Start**: Run `docker compose up -d` to start the extension.
4. **Success**: Write status file and return 200 OK.

### 3. Model Library Catalog

- **Location**: `INSTALL_DIR / "config" / "model-library.json"`
- **Purpose**: Whitelist of allowed models with SHA256 checksums.
- **Usage**: 
  - `/models` endpoint returns catalog.
  - `/activate` endpoint verifies model is in catalog before allowing download.

### 4. Error Handling Patterns

- **Progress Reporting**: `_write_progress(service_id, status, message, error="")` writes to `/tmp/dream-server-progress-<service_id>`.
- **Error Truncation**: Previously used `stderr[:500]` to truncate error messages.
- **Logging**: Uses Python `logging` module with `logger` instance.

## Relevant Patterns for PR #1057

### 1. Bind Mount Resolution

The `_precreate_data_dirs` function resolves bind mount sources to create directories. PR #1057 adds handling for:
- **Compose long-form mounts** (`dict` with `type`, `source`, etc.)
- **Unresolvable sources** (`~`, `$`, `` ` ``, `\`) — skipped to avoid unsafe path expansion.

### 2. Docker Compose Pull Optimization

Previously, `docker compose pull` was called with all flags, including compose files from *other* extensions. This caused unnecessary refetching.

PR #1057 introduces `_is_other_ext_compose()` to filter out other extensions' compose files during pull, keeping only:
- Base compose files
- GPU overlay compose files
- The current extension's own compose file

### 3. Model Catalog Error Handling

Previously, missing/malformed `model-library.json` was silently treated as "no models allowed."

PR #1057 distinguishes:
- **Catalog unreadable/malformed**: Return 500 with "Model catalog unavailable"
- **Catalog readable but model not listed**: Return 403 with "Model not in library catalog"

This distinction is critical for diagnosing broken installs vs. policy enforcement.

## AMD Relevance

- The PR does not touch GPU-specific code paths (ROCm, CUDA, etc.).
- The pull optimization may *benefit* AMD GPU users by reducing unnecessary network I/O during extension installs.
- No changes to `installer/gpu.py` or similar AMD-specific modules.

## Security Considerations

- **Path Traversal**: The new check for `~`, `$`, `` ` ``, `\` in bind mount sources prevents potential injection via environment variables or shell expansion.
- **Error Exposure**: Using `stderr[-500:]` (last 500 chars) instead of `[:500]` may expose more sensitive error text (e.g., credentials in error messages), but the PR author argues Docker Compose puts actual error text at the end of the stream.
