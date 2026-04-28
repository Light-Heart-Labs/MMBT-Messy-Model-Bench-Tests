# Triage Results for logalyzer Code Review

## Summary

- **Real issues:** 9
- **Fabricated issues:** 6

## Files

- `triage.json` — Machine-readable verdicts for all 15 issues
- `notes.md` — Detailed reasoning for each verdict
- `decisions/` — ADRs for borderline or non-obvious calls

## How to Read

Each issue in `triage.json` has:
- `verdict`: `"real"` (issue exists) or `"fabricated"` (issue does not exist)
- `evidence`: File/line citation for real issues, or explanation for fabricated ones

## Verification Method

1. Read the actual code in `/input/repo/logalyzer/`
2. Verify or refute each claim in `issue_report.md`
3. Cite specific lines for real issues
4. Explain why fabricated issues are not present (missing file, wrong line, code does X not Y)

## Key Findings

- **Issue 001** is real: `collections.Iterable` import fails on Python 3.10+
- **Issue 002** is real: `eval()` used in filters.py:59
- **Issue 003** is fabricated: No SQL code exists
- **Issue 004** is real: README claims tail mode but it's not implemented
- **Issue 005** is fabricated: `args.top` works correctly
- **Issue 006** is real: experimental.py is unused
- **Issue 007** is fabricated: No web.py or web interface exists
- **Issue 008** is fabricated: No 8192 character truncation
- **Issue 009** is real: `format_legacy()` is dead code
- **Issue 010** is fabricated: No concurrent access patterns
- **Issue 011** is fabricated: No double-counting of 3xx
- **Issue 012** is fabricated: No cache.py exists
- **Issue 013** is real: O(n²) list/string concatenation in io.py
- **Issue 014** is real: List membership in ip_allowlist_filter
- **Issue 015** is real: LogEntry not exported from __init__.py
