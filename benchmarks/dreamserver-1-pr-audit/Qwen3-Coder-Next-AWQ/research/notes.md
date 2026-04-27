# Working Notes — PR #1057 Audit

## Initial Observations

- PR title: "fix(host-agent): runtime hygiene — narrow pull, surface failures, normalize bind volumes"
- Commit message: Same as PR title
- Files changed: 1 (`dream-server/bin/dream-host-agent.py`)
- Lines changed: +73, -13

## Key Changes Identified

1. **Bind Mount Normalization** (lines 202-212)
   - Handles Compose long-form mounts (`dict` with `type`, `source`)
   - Skips unresolvable sources (`~`, `$`, `` ` ``, `\`)
   - Purpose: Prevent path traversal and ensure directories are created correctly

2. **Pull Optimization** (lines 1143-1173)
   - Filters out other extensions' compose files during `docker compose pull`
   - Uses `_is_other_ext_compose()` to determine if a compose file belongs to another extension
   - Reduces network I/O and install time

3. **Error Truncation Fix** (lines 1143, 1170, 1201)
   - Changed from `stderr[:500]` to `stderr[-500:]` (last 500 chars)
   - Rationale: Docker Compose puts actual error text at the end of the stream

4. **Model Catalog Error Handling** (lines 1236-1245, 1323-1357)
   - Distinguishes between "catalog unreadable/malformed" (500) and "catalog readable but model not listed" (403)
   - Adds `catalog_ok` sentinel to track catalog validity
   - Logs exceptions with `logger.exception()` for debugging

5. **Llama Server Error Handling** (lines 2204-2206)
   - Changed from logging error to raising `RuntimeError` with last 500 chars of stderr
   - Purpose: Surface failures that were previously swallowed

6. **Model Status Write** (lines 2223-2227)
   - Changed from silently ignoring `OSError` to logging warning
   - Purpose: Surface progress stall issues for debugging

## Questions Raised

1. **Why `stderr[-500:]` instead of `stderr[:500]`?**
   - PR author claims Docker Compose puts actual error text at the end.
   - Need to verify this assumption.

2. **Does `_is_other_ext_compose()` handle relative paths correctly?**
   - Function resolves paths relative to `INSTALL_DIR` if not absolute.
   - Need to verify edge cases (e.g., symlinks, nested extensions).

3. **Is the `catalog_ok` sentinel necessary?**
   - Could `library_path.exists()` and `try/except` handle this?
   - PR author argues conflating "missing" and "malformed" masks broken installs.

4. **Why raise `RuntimeError` in `_recreate_llama_server`?**
   - Previously logged error but continued; now fails fast.
   - Need to verify this doesn't break recovery flows.

5. **Does the bind mount normalization handle Windows paths?**
   - Check for `\` suggests Windows awareness, but code is Linux-only.
   - May be defensive, or leftover from shared codebase.

## Hypotheses

1. **Pull Optimization**: Should reduce install time for multi-extension setups.
   - Test: Install 3 extensions and measure pull time vs. baseline.

2. **Error Truncation**: `stderr[-500:]` may expose more sensitive data.
   - Risk: Credentials in error messages.
   - Mitigation: Review Docker Compose error output patterns.

3. **Model Catalog**: Distinguishing 500 vs. 403 improves debugging.
   - Test: Corrupt `model-library.json` and verify 500 response.

4. **Llama Server**: Raising `RuntimeError` may break recovery.
   - Test: Simulate `docker run` failure and verify agent behavior.

## Next Steps

1. Clone baseline (`main`) and PR branch to test.
2. Run installer in clean container to verify bind mount normalization.
3. Test pull optimization with multiple extensions.
4. Verify error truncation behavior with Docker Compose.
5. Corrupt model library and verify 500 vs. 403 distinction.
