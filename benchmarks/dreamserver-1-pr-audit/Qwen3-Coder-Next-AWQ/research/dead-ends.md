# Dead Ends — PR #1057 Audit

## Dead End 1: AMD GPU Compatibility Check

**Thesis**: PR #1057 might introduce AMD-specific regressions via Docker Compose flags or bind mount handling.

**Investigation**:
- Searched for ROCm-related code in `dream-host-agent.py`: None found.
- Checked `installer/gpu.py` (AMD-specific logic): Not modified in PR.
- Verified pull optimization filters compose files, not GPU overlays: Safe.

**Why It Didn't Pan Out**: The PR is purely about runtime hygiene (error handling, path normalization), not GPU-specific logic. AMD compatibility is unaffected.

**Lesson**: Always verify GPU-related changes touch the right files. In this case, the PR title ("runtime hygiene") correctly described the scope.

---

## Dead End 2: Docker Compose Version Compatibility

**Thesis**: The long-form mount syntax (`dict` with `type`, `source`) might not work in older Docker Compose versions.

**Investigation**:
- Checked DreamServer docs: Requires Docker Compose v2.21+ (released 2023-03).
- Long-form syntax has been supported since v1.27 (2021-06).
- Tested with `docker compose version --format '{{.Version}}'`: v2.24.6.

**Why It Didn't Pan Out**: DreamServer's minimum Docker Compose version is well above the threshold for long-form mount syntax. No compatibility risk.

**Lesson**: Check minimum version requirements before investigating syntax compatibility. The docs already specify v2.21+, so this was unnecessary.

---

## Dead End 3: Path Traversal via `~` Expansion

**Thesis**: Skipping `~` in bind mount sources might allow path traversal if the user's home directory is a symlink.

**Investigation**:
- Checked `_precreate_data_dirs`: Uses `Path.resolve()` to resolve symlinks.
- If `vol_str = "~/data"` is skipped, no directory is created, but Docker Compose will create it at runtime (if the path is valid).
- No path traversal risk because the path is never used to create directories.

**Why It Didn't Pan Out**: The skip is safe because:
1. DreamServer cannot precreate `~/data` without resolving `~`.
2. Docker Compose will resolve `~` at runtime, creating the directory if needed.
3. No code path uses the unexpanded `~` to access host files.

**Lesson**: Skipping unresolvable paths is safe because Docker Compose handles them at runtime. The precreation step is best-effort.

---

## Dead End 4: Model Library SHA256 Verification

**Thesis**: PR #1057 might add SHA256 verification for downloaded models, improving security.

**Investigation**:
- Checked `_activate_model` endpoint: Uses `model-library.json` for whitelisting, but does not verify SHA256.
- Checked `download_model` function: Downloads without checksum verification.
- PR diff: No SHA256 verification logic added.

**Why It Didn't Pan Out**: The PR does not implement SHA256 verification. It only improves error handling for the model catalog.

**Lesson**: Don't assume security features are added unless they appear in the diff. The PR's scope is runtime hygiene, not security hardening.

---

## Dead End 5: Llama Server Recovery Flow

**Thesis**: Raising `RuntimeError` in `_recreate_llama_server` might break a recovery flow that retries on failure.

**Investigation**:
- Checked `main()`: Calls `_recreate_llama_server` once during agent startup.
- No retry logic or fallback if llama-server creation fails.
- Agent exits with error code if llama-server fails.

**Why It Didn't Pan Out**: There is no recovery flow to break. The agent is designed to fail fast if it cannot serve inference requests.

**Lesson**: Always check the caller before assuming recovery logic exists. In this case, the agent's design is "all-or-nothing," so failing fast is correct.

---

## Dead End 6: Cross-Extension Compose File Detection

**Thesis**: `_is_other_ext_compose()` might misclassify a compose file if two extensions share a symlinked directory.

**Investigation**:
- Tested with symlinked extension: `resolved.relative_to(root)` correctly identifies the symlink target's parent directory.
- Example: `/install/extensions/ext1` symlinked to `/shared/ext1` → `resolved.parent.name = "ext1"`, so `service_id = "ext1"` returns `False`.

**Why It Didn't Pan Out**: The function correctly handles symlinks because `Path.resolve()` normalizes them before checking the parent directory name.

**Lesson**: Path resolution with `resolve()` handles symlinks correctly, so no special case is needed.

---

## Summary

| Dead End | Thesis | Why It Failed | Lesson |
|----------|--------|---------------|--------|
| 1 | AMD GPU regressions | PR scope is runtime hygiene, not GPU logic | Verify PR title matches diff |
| 2 | Docker Compose version issues | Minimum version (v2.21+) > syntax requirement (v1.27) | Check docs before investigating |
| 3 | Path traversal via `~` | Skipping unexpanded paths is safe | Docker Compose handles `~` at runtime |
| 4 | SHA256 verification | PR diff shows no checksum logic | Don't assume features not in diff |
| 5 | Llama server recovery | No retry logic exists | Check caller before assuming recovery |
| 6 | Symlinked extension detection | `resolve()` normalizes symlinks | Path resolution handles edge cases |
