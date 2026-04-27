# PR #1022 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard-api): async hygiene in routers/extensions.py

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Fixes three async-hygiene defects in `routers/extensions.py`: blocking urllib calls on the event-loop thread, over-broad `except Exception` catches that swallow programmer errors, and a fire-and-forget executor future that silently discards cleanup failures.

## Why
- `extension_logs` and `extensions_catalog` called `urllib.urlopen` directly on the async event loop. The Console modal polls every 2 s with a 30 s agent timeout, so a single slow host-agent response could block the entire dashboard-api event loop for up to 30 s.
- `_call_agent`, `_call_agent_invalidate_compose_cache`, and `_call_agent_compose_rename` caught `except Exception`, meaning `AttributeError`, `TypeError`, and other programmer bugs were silently swallowed and logged as "host agent unreachable" — masking real bugs.
- `_cleanup_stale_progress` was dispatched via `run_in_executor(None, ...)` with the returned Future immediately discarded, so any unhandled exception inside the cleanup only produced an opaque "Future exception was never retrieved" warning in stderr with no context.

## How
- Extracted `_fetch_agent_logs(url, headers, data, timeout) -> str` — a plain synchronous function that can be safely offloaded via `asyncio.to_thread`.
- `extension_logs`: replaced inline `urllib.urlopen` block with `await asyncio.to_thread(_fetch_agent_logs, ...)`, matching the existing `asyncio.to_thread` pattern already used in `main.py`'s `api_settings_env_save`.
- `extensions_catalog`: replaced direct `_check_  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
