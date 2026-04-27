# code-task-starter — design notes (internal, NOT mounted into the agent's view)

What was deliberately seeded into `inputs/code-task-starter/`. Used to verify the grader detects what we expect, and to compare agent triage reports against ground truth.

## Issues seeded

### Functional bugs (each should trigger a failing test in the starter test suite)

1. **`logalyzer/parser.py` MONTH_NAMES table**: `"Jul"` is missing from the array. Causes `parse_timestamp` to return wrong months for any date Jul-Dec (off by one for Aug-Dec, raises ValueError for Jul).
   - Triggered by: `test_timestamp_july_parses_correctly` (assert month==7) and `test_timestamp_january_parses_correctly` may pass since Jan is at index 0, but other month tests wouldn't.
   - Severity: high (data-corruption — wrong month assignment is silent)

2. **`logalyzer/filters.py::status_filter`**: compares `entry.status` (int) directly to the parameter, but the CLI passes `--status` as a string, so `entry.status == "200"` is False even for status 200.
   - Triggered by: `test_status_filter_works_with_cli_string_input` (passes string "404", expects match)
   - Severity: high (whole filter doesn't work from the CLI)

3. **`logalyzer/filters.py::url_regex_filter`**: uses `rx.match()` (anchored to start) instead of `rx.search()` (substring). Pattern `"admin"` won't match URL `/api/admin/users`.
   - Triggered by: `test_url_regex_finds_substring_match` (asserts `/api/admin/users` matches "admin")
   - Severity: medium (subtle behavior mismatch with user expectation)

4. **`logalyzer/aggregate.py::by_hour`**: uses `time.localtime()` to bucket UTC timestamps, so results depend on host TZ.
   - Triggered by: `test_by_hour_uses_utc_not_local_time` (expects 12 UTC entries to land in bucket 12, fails on hosts not at UTC)
   - Severity: medium (correctness depends on environment)

5. **`logalyzer/output.py::to_json`**: builds JSON by manual string interpolation, doesn't escape quotes/backslashes/control chars in URLs or other fields. Will produce invalid JSON for any URL with a quote in it.
   - Not triggered by an existing test (tests/test_output.py doesn't exist) — this is a coverage gap that the agent should notice.
   - Severity: high (silent data corruption for any URL with special chars)

### Deprecated / will-break-on-modern-Python

6. **`logalyzer/filters.py`**: `from collections import Iterable` — removed in Python 3.10. Causes ImportError at import time on 3.10+.
   - Triggered by: any test that imports filters (so basically all of test_filters and test_aggregate via cli — though the `Iterable` import isn't actually used in the code, the import itself fails)

   Actually the comment says "used by some downstream callers; ensure compatibility" which is a lie — nothing imports `Iterable` from `filters.py`. So the agent should both fix the import AND remove the dead reference.
   - Severity: high (breaks the import of a core module on modern Python)

### Performance issues (should be measurable via benchmarks/bench.py)

7. **`logalyzer/io.py::load`**: reads the entire file with `f.read()`, then iterates character-by-character with `+=` string concat (O(n²)) and list `result = result + [entry]` (also O(n²) on list).
   - Triggered by: bench.py timings on a 50 MB log will be ~10-30× slower than they should be
   - Reasonable fix: rewrite as line-streaming with `for line in f:` and `result.append(entry)`
   - Severity: medium-high (silent — works correctly on small files, bites at scale)

8. **`logalyzer/filters.py::ip_allowlist_filter`**: stores allowlist as whatever iterable is passed in, falls back to linear scan with `in`. Should convert to set for O(1) lookups.
   - Not triggered by any standard test, but observable in benchmarks if the agent writes one with a large allowlist.
   - Severity: low-medium (matters at scale)

### Dead code

9. **`logalyzer/experimental.py`**: entire module never imported anywhere. ~30 LOC of unused code (`detect_anomalies`, `session_window`).
   - Severity: low (technical debt, lint signal)

10. **`logalyzer/utils.py::format_legacy`**: function never called from within the package. Comment claims "kept for any external scripts that may still depend on it" but there are no external callers.
   - Severity: low

### Documentation lies

11. **`README.md`**: claims "Real-time tail mode for live log streams" — not implemented. Also claims "Custom expression filtering for advanced queries" which does exist but uses `eval()` (security concern, see #12).
   - Severity: low (misleads users)

### Security

12. **`logalyzer/filters.py::expression_filter`**: uses `eval()` on user-supplied strings. The current `__builtins__: {}` restriction is weak — still allows attribute access on the `entry` object, and the CLI exposes this via `--expr`.
   - Should be replaced with a proper expression evaluator (ast.parse + walk, or a small DSL), or at minimum heavily restricted.
   - Severity: medium (CLI tool reading attacker-controlled flags is an unusual threat model, but the pattern is wrong)

### Coverage gaps

13. **`tests/test_output.py`**: doesn't exist. `output.py` has 0% coverage. Triggers issue #5 going undetected.
14. **`tests/test_io.py`**: doesn't exist. The O(n²) bug in `load()` has no test pinning correctness.
15. **`tests/test_cli.py`**: doesn't exist. End-to-end CLI behavior has no test.

### Lint issues (ruff would surface these)

- Unused import `from datetime import timedelta` inside `parse_timestamp` (it's actually used, but in a non-obvious way at module level — depends on ruff config)
- The `from collections import Iterable` is unused — flag as F401 unused import
- Various long lines, unused variables in places
- The `format_legacy` and `chunked` in `utils.py` are unused if confirmed dead

## Expected delta after a successful pass

| metric | baseline (before) | after good agent (target) |
|---|---|---|
| `pytest` passing tests / total | 11 / 17 (or so — depends on import errors) | 17 / ≥17 (and ideally more, with new tests added for output/io/cli) |
| `pytest --cov` line coverage | ~50% (output.py/io.py untested) | ≥85% |
| `ruff check` issues | ~5-15 | 0 |
| benchmark seconds (50 MB log) | very slow — likely 30-90s due to O(n²) | <5s after streaming rewrite |
| `experimental.py` exists | yes (dead) | deleted (or wired up — agent's call, but must justify) |
| `eval()` in `expression_filter` | yes | replaced with safer eval |
| README "real-time tail mode" claim | present | removed or implemented |

## Grading rubric for the agent's deliverable

Programmatic (numeric):
- delta(passing_tests): -∞ to ∞, target +6 or more
- delta(line_coverage_%): target +≥35
- delta(ruff_issues): target ≤0 (i.e., decrease)
- delta(benchmark_seconds): target negative (faster), expect ≥5x speedup possible

Process artifacts (rubric):
- triage.md: did they catalogue the major issues? Bonus for finding non-obvious ones.
- One commit per logical fix? (16+ commits would be a strong signal of granular work)
- Dead-ends documented? (e.g., a refactor that was attempted then reverted)
- Architectural ADRs (e.g., chose to delete experimental.py vs keep it — either is fine if justified)
- README updates that reflect what changed
- benchmarks/bench.py-derived before/after numbers in audit/before-after.md

## Things the agent legitimately CAN'T fix without making judgment calls

- Whether to delete experimental.py vs wire it up vs leave it. Either is defensible if documented in a decision record.
- What to replace eval() with. Small DSL? Whitelist of attributes? Drop the feature entirely? Each is a real choice.
- Whether to add tests for end-to-end CLI behavior or just call it covered via integration of the parts.

These are exactly the things we want to see them reason about in /decisions/.
