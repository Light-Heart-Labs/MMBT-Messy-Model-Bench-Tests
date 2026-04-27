# Line-by-Line Review of PR #1057

## File: `dream-server/bin/dream-host-agent.py`

### Change 1: `_precreate_data_dirs` — Long-form volume support (lines 202-213)

**Before:**
```python
vol_str = str(vol).split(":")[0]
```

**After:**
```python
if isinstance(vol, dict):
    # Compose long-form mount; only bind mounts have a host source.
    if vol.get("type") != "bind":
        continue
    vol_str = vol.get("source", "")
else:
    vol_str = str(vol).split(":")[0]
# Skip sources compose does not pre-expand (env vars, home,
# backticks, Windows-style escapes) — we cannot resolve them safely.
if not vol_str or vol_str.startswith(("~", "$", "`", "\\")):
    continue
```

**Assessment:** ✅ Correct. The original code called `str(vol).split(":")[0]` on every volume entry. For long-form dict entries like `{"type": "bind", "source": "./data/foo", "target": "/bar"}`, `str()` produces `"{'type': 'bind', 'source': './data/foo', 'target': '/bar'}"` — the split on `:` would yield `"{'type'"` which is garbage. The new code correctly handles both short-form strings and long-form dicts. The skip logic for `~`, `$`, `` ` ``, `\` is sound — these are paths Docker Compose resolves at runtime but the host agent cannot resolve statically.

**Risk:** Low. The function already has graceful degradation (PyYAML import check, exception handling). The new skip conditions are conservative (they skip more, not less).

---

### Change 2: stderr tail-truncation in `_handle_install` (lines 1143, 1191, 1201)

**Before:** `result.stderr[:500]` (head-truncation)
**After:** `result.stderr[-500:]` (tail-truncation)

Three sites:
1. Line 1143: `post_install` hook failure
2. Line 1191: `docker compose pull` failure (warning log, 200 chars)
3. Line 1201: `docker compose up` failure

**Assessment:** ✅ Correct and important. Docker Compose output is structured with informational preamble (layer pulls, warnings) at the beginning and actual errors at the end. Head-truncation `[:500]` captures the preamble and misses the error. Tail-truncation `[-500:]` captures the actual error. This is a genuine bug fix.

**Risk:** None. This is purely a logging/display change. The error text is passed to `_write_progress` which writes JSON to a file — no behavioral change.

---

### Change 3: Narrow pull — `_is_other_ext_compose` (lines 1146-1180)

**What it does:** Filters out compose files belonging to other extensions from the `docker compose pull` step. The `up` step still uses full flags.

**Logic:**
1. Define `ext_roots` as `(EXTENSIONS_DIR.resolve(), USER_EXTENSIONS_DIR.resolve())`
2. `_is_other_ext_compose(fpath)`: Check if a path is inside an extension directory but NOT the current service's directory
3. Filter `flags` list: skip `-f <path>` pairs where the path is another extension's compose

**Assessment:** ✅ Correct in principle, but with one concern:

**Concern (minor):** The `_is_other_ext_compose` function is defined as a nested function inside `_run_install`, which is itself a nested function inside `_handle_install`. This means it's recreated on every install request. This is fine for correctness but slightly wasteful. Not a blocker.

**Concern (minor):** The check `resolved.parent.name == service_id` assumes the compose file's parent directory name matches the service ID. This is the convention used by DreamServer (extensions are in `extensions/services/<service_id>/compose.yaml`), so this is correct.

**Risk:** Low-Medium. If the filtering logic has a bug, it could cause `docker compose pull` to fail because it doesn't know about dependent services. However, the PR correctly notes that the `up` step uses full flags, so cross-service `depends_on` still resolves. The pull step is best-effort anyway (failure is non-fatal).

---

### Change 4: `_recreate_llama_server` — Raise RuntimeError on failure (lines 2201-2204)

**Before:**
```python
if result.returncode != 0:
    logger.error("Failed to create llama-server: %s", result.stderr)
else:
    logger.info("llama-server container created successfully")
```

**After:**
```python
if result.returncode != 0:
    logger.error("Failed to create llama-server: %s", result.stderr)
    raise RuntimeError(f"docker run failed: {result.stderr[-500:]}")
logger.info("llama-server container created successfully")
```

**Assessment:** ✅ Correct and important. The old code logged the error but continued execution, leading to a 5-minute health check timeout. The new code raises immediately, surfacing the error to the caller.

**Callers analysis:**
1. `_do_model_activate` (line 1684): Called inside `_in_container` path. The caller has a try/except that catches `Exception` and returns 500. ✅ Safe.
2. `_do_model_activate` rollback (line 1798): Called during rollback. The caller has a try/except that catches `Exception` and returns 500. ✅ Safe.
3. `_compose_restart_llama_server` (line 2004): Called when `.compose-flags` is absent. The caller `_compose_restart_llama_server` has its own `_run` helper that raises `RuntimeError`. The outer `_do_model_activate` catches `Exception`. ✅ Safe.

**Risk:** Low. All callers are wrapped in try/except blocks that handle `Exception`. The `RuntimeError` will be caught and surfaced as a 500 response, which is the correct behavior.

---

### Change 5: `_handle_model_list` — Surface catalog errors as 500 (lines 1233-1247)

**Before:**
```python
library = []
if library_path.exists():
    try:
        library = json.loads(library_path.read_text(encoding="utf-8")).get("models", [])
    except (json.JSONDecodeError, OSError):
        pass
```

**After:**
```python
library = []
if library_path.exists():
    try:
        library = json.loads(library_path.read_text(encoding="utf-8")).get("models", [])
    except (json.JSONDecodeError, OSError):
        logger.exception("Model library catalog unavailable")
        json_response(self, 500, {"error": "Model catalog unavailable"})
        return
```

**Assessment:** ✅ Correct. The old code silently swallowed errors and returned an empty catalog, which is misleading. The new code returns a 500 error, which correctly signals that the catalog is unavailable.

**Behavior change:** Clients that relied on an empty catalog response to detect "no catalog yet" will now get a 500. This is a breaking change but the old behavior was incorrect (masking errors).

**Risk:** Low. The catalog file is expected to exist on any non-fresh install. Fresh installs don't have the file, so `library_path.exists()` is False and the code returns an empty catalog (correct behavior).

---

### Change 6: `_handle_model_download` — Distinguish 403 from 500 (lines 1320-1363)

**Before:**
```python
if library_path.exists():
    try:
        lib = json.loads(library_path.read_text(encoding="utf-8"))
        # ... validation logic ...
    except (json.JSONDecodeError, OSError):
        pass
if not allowed:
    json_response(self, 403, {"error": "Model not in library catalog"})
    return
```

**After:**
```python
catalog_ok = False
if library_path.exists():
    try:
        lib = json.loads(library_path.read_text(encoding="utf-8"))
        catalog_ok = True
        # ... validation logic ...
    except (json.JSONDecodeError, OSError):
        logger.exception("Model library catalog unavailable")
        json_response(self, 500, {"error": "Model catalog unavailable"})
        return
if not catalog_ok:
    json_response(self, 500, {"error": "Model catalog unavailable"})
    return
if not allowed:
    json_response(self, 403, {"error": "Model not in library catalog"})
    return
```

**Assessment:** ✅ Correct. The old code conflated "catalog missing/unreadable" with "model not in catalog" — both returned 403. The new code correctly distinguishes:
- Catalog missing (file doesn't exist): 500
- Catalog unreadable/malformed: 500
- Model not in catalog: 403

**Risk:** Low. This is a more accurate error response. Clients that relied on 403 to detect "no catalog" will need to update, but the old behavior was incorrect.

---

### Change 7: `_write_model_status` — Log OSError (lines 2220-2225)

**Before:**
```python
except OSError:
    pass
```

**After:**
```python
except OSError as e:
    # Don't crash the activate flow; surface to the journal so operators
    # can diagnose why progress stalled.
    logger.warning("Failed to write model status to %s: %s", path, e)
```

**Assessment:** ✅ Correct. The old code silently swallowed write failures. The new code logs them at WARNING level, which is appropriate — the function should not crash the activate flow, but operators should be able to diagnose why progress stalled.

**Risk:** None. Purely a logging change.

---

## Summary of Findings

| Change | Correctness | Risk | AMD Impact |
|--------|------------|------|------------|
| Long-form volume support | ✅ Correct | Low | None |
| stderr tail-truncation | ✅ Correct | None | None |
| Narrow pull | ✅ Correct | Low-Medium | None |
| RuntimeError on recreate | ✅ Correct | Low | None |
| Model list 500 | ✅ Correct | Low | None |
| Model download 403/500 | ✅ Correct | Low | None |
| Model status logging | ✅ Correct | None | None |

**No AMD-specific code paths are touched.** The changes are all in the host agent's general error handling and compose flag logic, which apply equally to NVIDIA and AMD backends.
