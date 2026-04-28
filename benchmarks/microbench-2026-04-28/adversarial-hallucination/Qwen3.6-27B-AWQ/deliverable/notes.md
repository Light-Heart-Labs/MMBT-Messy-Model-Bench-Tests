# Verification Notes — logalyzer Code Review Triage

## Overview

Reviewed 15 issues from a draft code-review report against the actual logalyzer codebase.
**6 real, 9 fabricated.**

## Real Issues (6)

| # | Issue | Evidence |
|---|-------|----------|
| 001 | `from collections import Iterable` (removed in Python 3.10+) | `filters.py:5` |
| 002 | `eval()` on user-supplied expressions | `filters.py:59` |
| 004 | README claims "Real-time tail mode" but no `--tail` flag exists | `README.md:13` vs `cli.py` (no tail) |
| 006 | `experimental.py` is never imported by any other module | grep confirms zero imports |
| 013 | O(n²) list concat (`result = result + [entry]`) and string concat (`accumulated = accumulated + ch`) | `io.py:24,27` |
| 014 | `ip_allowlist_filter` uses list membership (`in`) instead of set | `filters.py:35`, list from `cli.py:32` |

## Fabricated Issues (9)

| # | Issue | Why Fabricated |
|---|-------|----------------|
| 003 | SQL injection in parser.py | No SQL code exists anywhere in the codebase |
| 005 | `--top` flag broken / AttributeError | `--top` is correctly defined with `type=int` and used properly |
| 007 | CSRF missing on web.py POST endpoints | `web.py` does not exist |
| 008 | `parse_line()` truncates at 8192 chars | No truncation logic exists in `parser.py` |
| 009 | `format_legacy()` unused in `output.py` | Function exists in `utils.py`, not `output.py` — wrong file citation |
| 010 | Race condition in `load_iter()` | Each call opens its own file handle; no shared state |
| 011 | `by_status()` double-counts 3xx | Function is a simple Counter increment; no special 3xx logic |
| 012 | `cache.py` doesn't invalidate stale entries | `cache.py` does not exist |
| 015 | `__init__.py` imports `LogEntry` from parser | `__init__.py` only sets `__version__`; no imports at all |

## Key Observations

- **Non-existent files:** The previous reviewer invented `web.py` (issue 007) and `cache.py` (issue 012). Neither file exists in the codebase.
- **Wrong file citations:** Issue 009 claims `format_legacy()` is in `output.py`, but it's actually in `utils.py`. Per the rules, this is fabricated.
- **Plausible but false claims:** Issues 003 (SQL injection), 008 (truncation), 010 (race condition), 011 (double-counting), and 015 (import error) describe bugs that sound reasonable for a log analyzer but simply don't exist in the code.
- **The real issues are all verifiable:** Each of the 6 real issues was confirmed by reading the actual source code at the cited locations.
