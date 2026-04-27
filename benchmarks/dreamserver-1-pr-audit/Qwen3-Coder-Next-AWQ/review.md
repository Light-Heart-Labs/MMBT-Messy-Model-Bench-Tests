# Line-by-Line Review — PR #1057

## File: `dream-server/bin/dream-host-agent.py`

### Lines 202-212: Bind Mount Normalization

**Original Code**:
```python
vol_str = str(vol).split(":")[0]
```

**New Code**:
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

**Review**:
- ✅ **Correct**: Handles both short-form (`str`) and long-form (`dict`) mounts.
- ✅ **Safe**: Skips unresolvable sources (`~`, `$`, `` ` ``, `\`) to prevent path traversal.
- ⚠️ **Defensive but broad**: Check for `\` (backslash) is overly broad for Linux. Add comment explaining it's defensive.
- ✅ **Logic**: `continue` on non-bind mounts is correct (only bind mounts need precreation).

**Recommendation**: Add comment explaining Windows path check is defensive.

---

### Lines 1143-1173: Pull Optimization

**Original Code**:
```python
pull_result = subprocess.run(
    ["docker", "compose"] + flags + ["pull", service_id],
    ...
)
```

**New Code**:
```python
def _is_other_ext_compose(fpath: str) -> bool:
    p = Path(fpath)
    if not p.is_absolute():
        p = INSTALL_DIR / p
    try:
        resolved = p.resolve()
    except OSError:
        return False
    if resolved.parent.name == service_id:
        return False
    for root in ext_roots:
        try:
            resolved.relative_to(root)
            return True
        except ValueError:
            continue
    return False

pull_flags: list = []
i = 0
while i < len(flags):
    if (flags[i] == "-f" and i + 1 < len(flags)
            and _is_other_ext_compose(flags[i + 1])):
        i += 2
        continue
    pull_flags.append(flags[i])
    i += 1

pull_result = subprocess.run(
    ["docker", "compose"] + pull_flags + ["pull", service_id],
    ...
)
```

**Review**:
- ✅ **Correct**: Filters out other extensions' compose files during pull.
- ✅ **Safe**: Resolves paths relative to `INSTALL_DIR` and checks against extension roots.
- ✅ **Edge Cases**: Handles relative paths, symlinks, and non-existent files.
- ✅ **No Impact on `up`**: Comment confirms `up` still uses full flags for dependencies.

**Recommendation**: None. This is a well-implemented optimization.

---

### Lines 1143, 1170, 1201: Error Truncation Fix

**Original Code**:
```python
error=result.stderr[:500]
```

**New Code**:
```python
error=result.stderr[-500:]
```

**Review**:
- ✅ **Correct**: Docker Compose appends errors to the end of stderr, so `[-500:]` captures more useful diagnostic info.
- ✅ **Verified**: Tested with `docker compose pull nonexistent:latest` — error text is at the end.
- ⚠️ **Security**: May expose more sensitive data (e.g., credentials in error messages), but this is acceptable for local development.

**Recommendation**: None. Assumption is correct.

---

### Lines 1236-1245, 1323-1357: Model Catalog Error Handling

**Original Code**:
```python
library = []
if library_path.exists():
    try:
        library = json.loads(library_path.read_text(encoding="utf-8")).get("models", [])
    except (json.JSONDecodeError, OSError):
        pass
```

**New Code**:
```python
# Load library. A missing file is fine (fresh install); an
# unreadable/malformed file is a real error — surface it as 500
# rather than silently returning an empty catalog.
library = []
if library_path.exists():
    try:
        library = json.loads(library_path.read_text(encoding="utf-8")).get("models", [])
    except (json.JSONDecodeError, OSError):
        logger.exception("Model library catalog unavailable")
        json_response(self, 500, {"error": "Model catalog unavailable"})
        return
```

**Review**:
- ✅ **Correct**: Distinguishes between "catalog unreadable/malformed" (500) and "catalog readable but model not listed" (403).
- ✅ **Safe**: Adds `catalog_ok` sentinel to track catalog validity.
- ✅ **Logging**: Uses `logger.exception()` for debugging.

**Recommendation**: None. This is a critical improvement for debugging broken installs.

---

### Lines 2204-2206: Llama Server Error Handling

**Original Code**:
```python
if result.returncode != 0:
    logger.error("Failed to create llama-server: %s", result.stderr)
else:
    logger.info("llama-server container created successfully")
```

**New Code**:
```python
if result.returncode != 0:
    logger.error("Failed to create llama-server: %s", result.stderr)
    raise RuntimeError(f"docker run failed: {result.stderr[-500:]}")
logger.info("llama-server container created successfully")
```

**Review**:
- ✅ **Correct**: Raises `RuntimeError` to fail fast if llama-server creation fails.
- ✅ **Safe**: No recovery flow exists, so failing fast is correct.
- ✅ **Consistent**: Uses `stderr[-500:]` like other error handling.

**Recommendation**: None. Failing fast is the right behavior.

---

### Lines 2223-2227: Model Status Write

**Original Code**:
```python
except OSError:
    pass
```

**New Code**:
```python
except OSError as e:
    # Don't crash the activate flow; surface to the journal so operators
    # can diagnose why progress stalled.
    logger.warning("Failed to write model status to %s: %s", path, e)
```

**Review**:
- ✅ **Correct**: Logs warning instead of silently ignoring `OSError`.
- ✅ **Safe**: Doesn't crash the activate flow; just logs the issue.

**Recommendation**: None. Improved debugging.

---

## Overall Assessment

| Aspect | Score | Notes |
|--------|-------|-------|
| Correctness | 5/5 | No correctness issues |
| Safety | 5/5 | No security or stability issues |
| AMD Compatibility | 5/5 | No AMD-specific code touched |
| Test Coverage | 3/5 | No new tests added |
| Documentation | 4/5 | Comments are good; add one for Windows path check |
| Reversibility | 5/5 | Changes are additive; no breaking changes |

**Verdict**: **MERGE** after adding comment for Windows path check.
