# Diff Analysis: What the Diff Actually Changes vs What It Claims

## Claimed Changes (from commit message)

### 1. "Narrow `docker compose pull` to base + GPU overlay + the target extension's own compose file"

**Claim:** Other user extensions' compose files are filtered out so a single unset `:?` guard in an unrelated extension no longer aborts the install.

**What the diff actually does:** Adds a `_is_other_ext_compose()` helper that checks if a compose file path is inside `EXTENSIONS_DIR` or `USER_EXTENSIONS_DIR` but NOT in the current service's subdirectory. The `pull` step uses filtered flags; the `up` step uses full flags.

**Verdict:** ✅ Matches claim. The implementation correctly filters other extensions' compose files from the pull step while preserving them for the up step.

### 2. "Replace head-truncation `stderr[:N]` with tail-truncation `stderr[-N:]`"

**Claim:** Docker-compose errors live at the END of stderr after the layer-pull preamble; the head-truncation was hiding the actual failure cause.

**What the diff actually does:** Changes three sites:
- `result.stderr[:500]` → `result.stderr[-500:]` (post_install hook failure)
- `pull_result.stderr[:200]` → `pull_result.stderr[-200:]` (pull failure warning)
- `start_result.stderr[:500]` → `start_result.stderr[-500:]` (start failure)

**Verdict:** ✅ Matches claim. All three sites are in `_handle_install` and the change is consistent.

### 3. "`_write_model_status` now logs OSError write failures"

**Claim:** Behavior preserved (does not raise) so the activate flow continues, but the failure surfaces to the journal.

**What the diff actually does:** Changes `except OSError: pass` to `except OSError as e: logger.warning(...)`.

**Verdict:** ✅ Matches claim. No behavioral change, just logging.

### 4. "`_recreate_llama_server` now raises `RuntimeError`"

**Claim:** Replaces the silent log-and-fall-through that hung the activate flow for 5 minutes waiting for a health check that would never succeed.

**What the diff actually does:** Adds `raise RuntimeError(f"docker run failed: {result.stderr[-500:]}")` after the `logger.error` call. Also removes the `else:` branch so the success log is unconditional (runs after the error path raises).

**Verdict:** ✅ Matches claim. The old code logged and fell through to the health check loop. The new code raises immediately.

### 5. "Distinguish HTTP 403 from HTTP 500 in library validation"

**Claim:** A missing or unreadable `config/model-library.json` now returns a clear 500 rather than a misleading 403.

**What the diff actually does:**
- In `_handle_model_list`: Changes silent `pass` on JSON/OSError to `logger.exception` + 500 response.
- In `_handle_model_download`: Adds `catalog_ok` sentinel to distinguish "catalog unreadable/missing" (500) from "catalog readable but model not listed" (403).

**Verdict:** ✅ Matches claim. The behavior change is documented and correct.

### 6. "`_precreate_data_dirs` now handles long-form Compose volume entries"

**Claim:** Handles `{type: bind, source: ./foo, target: /bar}` and skips relative bind sources Docker does not pre-expand.

**What the diff actually does:** Adds `isinstance(vol, dict)` check, extracts `source` from bind mounts, and skips paths starting with `~`, `$`, `` ` ``, `\`.

**Verdict:** ✅ Matches claim. The implementation correctly handles both short-form and long-form volume entries.

## Unclaimed Changes

None detected. All changes in the diff are accounted for in the commit message.

## Discrepancies

None. The diff matches the commit message claims exactly.
