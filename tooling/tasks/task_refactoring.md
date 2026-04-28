You have access to a Python codebase mounted read-only at `/input/repo/`. It's a small CLI tool called **logalyzer** for analyzing web server access logs. The codebase has a working but slightly accreted internal structure: `parser.py` mixes log-line parsing with format-detection logic, `output.py` mixes JSON/CSV/plain rendering with a legacy "format_legacy" function, and `utils.py` is a grab-bag of helpers that don't share a domain.

You have a fresh Linux VM with a Python 3.11 environment, standard CLI tools, git, and the toolchain (pytest, pytest-cov, ruff). No time limit.

Your task: **perform one targeted, behavior-preserving refactor** on this codebase. Specifically:

**Target refactor: separate `output.py` into focused modules.**

The current `output.py` mixes (1) JSON serialization, (2) CSV serialization, (3) plain-text formatting, and (4) the legacy `format_legacy()` function that's only used for backwards compatibility. Split this into a `logalyzer/output/` package with one module per concern. Specifically:

```
logalyzer/output/
  __init__.py         Re-exports the public API (whatever the rest of the codebase imports today)
  json_renderer.py    JSON output
  csv_renderer.py     CSV output
  plain_renderer.py   Plain-text output
  legacy.py           format_legacy() and any backward-compat shims
```

Constraints:

1. **Behavior must be byte-identical for all current call sites.** Every import currently of the form `from logalyzer.output import X` must still work. The existing test suite must pass without modification — the refactor is NOT allowed to change observable behavior. (You CAN run pytest yourself to verify; you may not modify the tests.)
2. **No new dependencies.** Stay within stdlib + what's already in `pyproject.toml`.
3. **No bug fixes.** If you encounter a bug, document it in `dead-ends.md` but don't fix it. The refactor is structural; fixing bugs is out of scope.
4. **Don't change unrelated code.** Only `logalyzer/output.py` may be split. The rest of the package, the tests, the benchmarks — leave them alone.

You may NOT do any of the following (out of scope, even if tempting):
- Refactor `parser.py` or `utils.py` (too much surface area; leave them as-is)
- Modernize deprecated imports (`collections.Iterable` and similar; that's a different task)
- Rewrite the CLI entry point in `cli.py`
- Change the data classes or the public API surface

Everything you produce must live in a new git repository at `/workspace/`. Commit early, commit often. Each step of the refactor should be one commit so a reviewer can follow the move.

## Required repo structure

```
/logalyzer/             The package, with output.py replaced by output/ subpackage
  output/               New subpackage (per the spec above)
  ... rest unchanged
/tests/                 The starter test suite, byte-identical to input
/decisions/             ADR-style records:
                          0001-why-split-output.md
                          0002-public-api-shape.md (what gets re-exported, why)
                          NNNN-...md for any other non-obvious choice
/research/
  notes/                Working notes, dated
  questions.md          Things you weren't sure about and how you resolved them
  dead-ends.md          Refactor approaches you tried and reverted, with why
CHANGELOG.md            Summary of the refactor: before/after structure, what moved where, why
```

## Verification — run these yourself before calling done()

1. `pytest -q` from `/workspace/` — must pass with the same number of tests as the starter
2. `python -c "from logalyzer.output import format_legacy; print(format_legacy)"` — must work (the legacy helper must still be importable from its old location)
3. `git diff /input/repo/tests /workspace/tests` — must be empty (you didn't modify tests)
4. `git diff /input/repo/logalyzer/parser.py /workspace/logalyzer/parser.py` etc. for non-output files — must be empty

Document the verification results in CHANGELOG.md.

When you're done, the final commit tags a release. A reviewer should be able to clone the repo and verify the four checks above pass in <2 minutes.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Commit each logical step of the move as a separate commit. Do not ask for clarification — make reasonable choices and document them in `/decisions/`.
