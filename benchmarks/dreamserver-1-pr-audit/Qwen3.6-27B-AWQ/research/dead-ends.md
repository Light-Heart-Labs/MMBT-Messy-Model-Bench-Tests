# Dead Ends

## 1. Attempted to reproduce the stderr head-truncation bug

**Thesis:** The PR claims that `stderr[:500]` hides the actual error because Docker Compose puts errors at the end of stderr.

**Investigation:** I attempted to create a Docker Compose setup that would produce a long stderr output to verify that head-truncation hides the error. However, the sandbox environment doesn't have Docker Compose configured with the DreamServer stack, so I couldn't run a real install flow.

**Resolution:** Accepted the claim based on code analysis. Docker Compose's output format is well-documented: it prints layer pull progress at the beginning and errors at the end. The head-truncation `[:500]` would capture the progress preamble and miss the error. This is a well-known pattern.

## 2. Attempted to verify the `_recreate_llama_server` 5-minute hang

**Thesis:** The PR claims that the silent log-and-fall-through in `_recreate_llama_server` causes a 5-minute hang waiting for a health check that will never succeed.

**Investigation:** I traced the call chain: `_do_model_activate` → `_recreate_llama_server` → health check loop (60 attempts × ~5s = ~5 min). The old code logged the error but didn't raise, so the health check loop would run to completion.

**Resolution:** Accepted the claim based on code analysis. The health check loop is at lines 1718-1780 and runs for up to 60 attempts. Without a successful container recreation, the health check will always fail, causing a 5-minute delay before the error is surfaced.

## 3. Attempted to test the long-form volume handling

**Thesis:** The PR claims that long-form Compose volume entries (`{type: bind, source: ./foo, target: /bar}`) were not handled by the original code.

**Investigation:** I attempted to create a test extension with long-form volume entries and verify that `_precreate_data_dirs` would fail to create the directories. However, the sandbox doesn't have the full DreamServer extension structure.

**Resolution:** Accepted the claim based on code analysis. The original code called `str(vol).split(":")[0]` on dict entries, which produces garbage output. The new code correctly handles both short-form strings and long-form dicts.
