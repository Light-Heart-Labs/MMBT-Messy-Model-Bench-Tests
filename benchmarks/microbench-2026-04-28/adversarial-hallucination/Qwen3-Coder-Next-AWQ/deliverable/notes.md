# Notes on Issue Verification

## Issue 001 - Real
Confirmed: `from collections import Iterable` at line 5 of filters.py fails on Python 3.10+. The correct import is `from collections.abc import Iterable`.

## Issue 002 - Real
Confirmed: `eval()` is used at filters.py:59 with restricted `__builtins__`. While this is safer than unrestricted eval, it's still a security risk and should be replaced with a proper expression parser.

## Issue 003 - Fabricated
No SQL-related code exists. The codebase only parses logs and outputs JSON/CSV/text. No database export pipeline is present.

## Issue 004 - Real
README.md line 9 claims "Real-time tail mode for live log streams" but there is no `--tail` flag and no streaming logic in the code. This is a false claim.

## Issue 005 - Fabricated
`args.top` is correctly parsed in cli.py:17 with `type=int, default=None` and used correctly in cli.py:64. No AttributeError occurs.

## Issue 006 - Real
experimental.py exists but is never imported by any module. It contains unused functions for anomaly detection and session windows.

## Issue 007 - Fabricated
No `web.py` file exists. The codebase is purely CLI-based with no web interface, CSRF tokens, or POST endpoints.

## Issue 008 - Fabricated
No 8192 character limit exists in parser.py. The `parse_line()` function processes the entire input line without truncation.

## Issue 009 - Real
`format_legacy()` in utils.py:21 is defined but never called or imported anywhere in the codebase. It's dead code retained for backwards compatibility claims.

## Issue 010 - Fabricated
No concurrent access or locking is implemented. `load_iter()` uses Python's file iterator and `load()` reads the entire file at once—neither has thread-safety issues because they're not designed for concurrent use.

## Issue 011 - Fabricated
`by_status()` simply iterates and counts with Counter. There's no special handling for 3xx redirects and no double-counting logic.

## Issue 012 - Fabricated
No `cache.py` file exists. The codebase has no caching mechanism, so stale cache invalidation is not applicable.

## Issue 013 - Real
Confirmed: io.py uses `result = result + [entry]` (O(n²) list concatenation) and `accumulated = accumulated + ch` (character-by-character string concatenation). Both are inefficient for large files.

## Issue 014 - Real
Confirmed: `ip_allowlist_filter()` uses `entry.ip in allowlist` directly. When `allowlist` is a list (from argparse's `--ip`), membership tests are O(n) instead of O(1). Converting to a set would improve performance.

## Issue 015 - Real
Confirmed: `__init__.py` does not export `LogEntry`. Attempting `from logalyzer import LogEntry` raises ImportError. The module only defines `__version__`.
