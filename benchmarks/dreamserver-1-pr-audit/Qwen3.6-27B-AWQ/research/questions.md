# Questions and Resolutions

## Q1: Does `_recreate_llama_server` being called from `_compose_restart_llama_server` create a double-raise scenario?

**Context:** `_compose_restart_llama_server` has its own `_run` helper that raises `RuntimeError`. It calls `_recreate_llama_server` as a fallback when `.compose-flags` is absent.

**Resolution:** No double-raise. The `_run` helper is used for the compose path (stop + up). The `_recreate_llama_server` call is in the `else` branch (no compose flags). They are mutually exclusive paths.

## Q2: Is the `catalog_ok` sentinel in `_handle_model_download` necessary, or could we use `library_path.exists()` directly?

**Context:** The PR adds a `catalog_ok = False` sentinel to distinguish "file exists but is malformed" from "file doesn't exist."

**Resolution:** The sentinel is necessary. Without it:
- File doesn't exist → `if library_path.exists()` is False → skip to `if not allowed` → 403 (wrong, should be 500)
- File exists but malformed → `except` catches it → `catalog_ok` stays False → 500 (correct)
- File exists and valid → `catalog_ok = True` → proceed to check `allowed`

The sentinel correctly handles the "file doesn't exist" case by returning 500, which is the intended behavior (a missing catalog is a broken install, not a policy denial).

## Q3: Does the `_is_other_ext_compose` function handle relative paths correctly?

**Context:** The function converts relative paths to absolute using `INSTALL_DIR / p`.

**Resolution:** Yes. Compose flags from `resolve_compose_flags()` are relative to `INSTALL_DIR`. The function correctly resolves them to absolute paths before checking if they're inside extension directories.

## Q4: Is the `logger.exception` call appropriate for JSON decode errors?

**Context:** The PR adds `logger.exception("Model library catalog unavailable")` for `json.JSONDecodeError` and `OSError`.

**Resolution:** Yes. `logger.exception` includes the traceback, which is useful for debugging malformed JSON files. The message is clear and the log level (ERROR, which is what `exception` uses) is appropriate for a catalog that should be readable.

## Q5: Does the narrow-pull change affect the `--no-deps` flag in the `up` step?

**Context:** The `up` step uses `--no-deps` flag. Does filtering compose files from the pull step affect dependency resolution?

**Resolution:** No. The `up` step uses full flags (not filtered), so cross-service `depends_on` still resolves. The `--no-deps` flag means "don't start dependencies," which is correct for installing a single extension. The pull step is best-effort anyway.
