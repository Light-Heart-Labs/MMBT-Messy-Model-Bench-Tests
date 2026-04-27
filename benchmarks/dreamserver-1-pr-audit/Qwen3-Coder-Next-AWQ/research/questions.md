# Questions Log — PR #1057 Audit

## Q1: Why `stderr[-500:]` instead of `stderr[:500]`?

**Question**: The PR changes error truncation from `stderr[:500]` (first 500 chars) to `stderr[-500:]` (last 500 chars). The commit message says "surface failures," but why is the *end* of stderr more important than the beginning?

**Investigation**:
- Checked Docker Compose documentation: Error messages are typically appended to stderr, with header lines (e.g., "Pulling from...") at the start.
- Tested with simulated Docker Compose failure: Actual error (e.g., "no such file or directory") appears at the end of stderr.
- Verified with `docker compose pull nonexistent:latest`: Error text is at the end.

**Resolution**: PR author's assumption is correct. Docker Compose puts actual error text at the end of stderr, so `[-500:]` captures more useful diagnostic info.

**Assumption**: This holds for the specific failure modes in DreamServer (missing images, invalid compose files). For network errors, the header may contain useful context (e.g., "connection refused"), but those are rare in local installs.

---

## Q2: Does `_is_other_ext_compose()` handle relative paths correctly?

**Question**: The function resolves paths relative to `INSTALL_DIR` if not absolute. What if a compose file uses `../other-ext/docker-compose.yml`? Could this bypass the filter?

**Investigation**:
- Checked code: `p = Path(fpath)` then `p = INSTALL_DIR / p` if not absolute.
- `p.resolve()` normalizes `..` and symlinks, so `../other-ext` becomes `/install/extensions/other-ext`.
- `resolved.relative_to(root)` checks if the resolved path is under `EXTENSIONS_DIR` or `USER_EXTENSIONS_DIR`.

**Resolution**: Yes, relative paths are handled correctly. `Path.resolve()` normalizes `..` before checking against extension roots.

**Edge Case**: If `INSTALL_DIR` itself is a symlink, `resolve()` will follow it, which is correct for this use case.

---

## Q3: Is the `catalog_ok` sentinel necessary?

**Question**: The PR adds a `catalog_ok` flag to distinguish "catalog unreadable/malformed" (500) from "catalog readable but model not listed" (403). Could this be achieved with `library_path.exists()` and `try/except`?

**Investigation**:
- Original code: If `library_path.exists()` is False, `allowed` stays False → 403.
- If `library_path.exists()` is True but parsing fails, `pass` → `allowed` stays False → 403.
- Conflation: Missing file and malformed file both return 403.

**Resolution**: Yes, the sentinel is necessary. Without it, a broken install (e.g., corrupted `model-library.json`) appears as a policy violation (403), not a system error (500). Operators would waste time checking model names instead of fixing the catalog.

**Test Plan**: Corrupt `model-library.json` and verify 500 response.

---

## Q4: Why raise `RuntimeError` in `_recreate_llama_server`?

**Question**: The PR changes `_recreate_llama_server` to raise `RuntimeError` instead of logging the error and continuing. Could this break recovery flows?

**Investigation**:
- Checked caller: `_recreate_llama_server` is called from `main()` during agent startup.
- If llama-server creation fails, the agent cannot serve inference requests.
- Raising `RuntimeError` ensures the agent fails fast, preventing partial startup.

**Resolution**: The change is safe. The agent has no fallback if llama-server fails, so failing fast is correct.

**Risk**: If `docker run` fails due to a transient issue (e.g., Docker daemon restart), the agent won't retry. However, the agent is typically started once at boot, so this is acceptable.

---

## Q5: Does the bind mount normalization handle Windows paths?

**Question**: The PR checks for `\` (backslash) in bind mount sources, suggesting Windows awareness. But DreamServer is Linux-only. Is this defensive, or leftover from shared code?

**Investigation**:
- Checked codebase: No Windows-specific code in `dream-host-agent.py`.
- The check is in `_precreate_data_dirs`, which runs on the host (Linux).
- Backslash is a valid character in Linux filenames, so the check is overly broad.

**Resolution**: The check is defensive but unnecessary. It will skip valid Linux paths containing `\` (rare but possible). However, it prevents accidental path traversal via Windows-style escapes (e.g., `\..\secret`), so it's a reasonable safety net.

**Recommendation**: Add a comment explaining the check is defensive, not required for Linux.

---

## Q6: Does the pull optimization affect cross-service dependencies?

**Question**: The PR filters out other extensions' compose files during `pull`, but the `up` step still uses all flags. Could this break `depends_on`?

**Investigation**:
- Docker Compose `pull` only downloads images; it doesn't resolve dependencies.
- `depends_on` is resolved during `up`, not `pull`.
- The PR comment says: "The `up` step below keeps full `flags` so cross-service `depends_on` still resolves."

**Resolution**: No risk. The optimization is safe because `pull` and `up` have different dependency requirements.

---

## Q7: What is the impact of skipping unresolvable bind mount sources?

**Question**: The PR skips bind mount sources starting with `~`, `$`, `` ` ``, `\`. What if a user intentionally uses these (e.g., `$HOME/data`)?

**Investigation**:
- Docker Compose resolves `$HOME` and `~` at *runtime*, not at `docker compose up` time.
- DreamServer precreates directories *before* `up`, so it needs concrete paths.
- If the source is unresolvable, DreamServer cannot precreate the directory.

**Resolution**: The skip is correct. Users must use concrete paths (e.g., `/home/user/data`) for DreamServer to precreate them. Environment variable expansion is deferred to Docker Compose at runtime.

**Trade-off**: Users cannot use `$HOME` in bind mounts, but this is a known limitation of DreamServer's precreation approach.

---

## Summary

| Question | Resolution | Risk | Action |
|----------|------------|------|--------|
| Q1: Error truncation | Assumption correct | Low | None |
| Q2: Relative paths | Handled correctly | None | None |
| Q3: Catalog sentinel | Necessary | Medium | Test 500 vs. 403 |
| Q4: Llama RuntimeError | Safe | Low | None |
| Q5: Windows paths | Defensive but safe | Low | Add comment |
| Q6: Cross-service deps | No impact | None | None |
| Q7: Unresolvable sources | Correct skip | Medium | Document limitation |
