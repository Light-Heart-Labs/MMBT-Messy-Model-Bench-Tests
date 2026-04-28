You have access to a Python codebase mounted read-only at `/input/repo/`. It's a small CLI tool called **logalyzer** for analyzing web server access logs. The codebase has working tests for some modules and **deliberately uncovered modules** elsewhere — `experimental.py` has 0% coverage, `format_legacy()` in `output.py` is uncovered, and several utility functions in `utils.py` have no test for their edge cases.

You have a fresh Linux VM with a Python 3.11 environment, standard CLI tools, git, and the toolchain (pytest, pytest-cov, ruff). No time limit.

Your task: **add high-value tests** for under-covered code in this codebase. Every test you write must:

1. **Pass** when run against the current codebase
2. **Actually exercise the code under test** — coverage % must measurably increase
3. **Not change behavior** — you are NOT fixing bugs, NOT modernizing deprecated code, NOT refactoring. If you find a bug, document it but don't fix it (the test should pass against current behavior, even if that behavior is wrong).
4. **Avoid trivial tests** that don't add real signal — `assert add(2, 2) == 4` style is not high-value. Test edge cases, error paths, boundary conditions, integration between modules.

The repo at the end should be the starter codebase **plus** your added test files, with measurably higher test coverage and zero baseline test regressions.

Everything you do must live in a new git repository at `/workspace/`. Commit early, commit often, write real commit messages explaining *why* not *what*.

## Required repo structure

```
/logalyzer/             The starter package, untouched (you may not modify any file here)
/tests/                 Tests — original starter tests preserved, plus your additions
/decisions/             Numbered ADR-style records: which modules you targeted, why; what you chose to NOT test, why
/research/
  notes/                Working notes, dated
  questions.md          Things you weren't sure about
  dead-ends.md          Tests you wrote and removed (e.g., unstable, didn't actually exercise code, found ambiguity)
CHANGELOG.md            Summary of what changed (which test files added, coverage delta)
```

## Rules of the road

- **Coverage % must go up.** Run `pytest --cov=logalyzer` before and after; document both numbers in CHANGELOG.md.
- **Baseline tests must still pass.** All tests that passed before must still pass. If you find a starter test that's flaky or wrong, document it in `dead-ends.md` but don't modify it.
- **No production code changes.** The `/logalyzer/` package files at the end must be byte-identical to the input. Only `/tests/` may differ.
- **Commit messages explain why.** "Add test for parse_clf with empty input — surfaces silent-empty-return behavior that wasn't covered" is good. "Add test_parser.py" is bad.
- **Test the dead code intentionally.** `experimental.py` may be marked "experimental"; testing it is fine if the goal is increasing coverage and exercising the code path. Document in an ADR whether you think the dead code should be kept or removed (but don't remove it — that's refactoring, out of scope).
- **Edge cases matter.** Testing the happy path adds little signal. Testing what happens with an empty file, a malformed line, an out-of-range date, an invalid IP, a unicode URL — that's where the value is.

## Reproducibility

Test scripts in `/tests/` must be runnable by `pytest` with no special flags or environment setup beyond the starter's `pyproject.toml`. Don't introduce new dependencies.

When you're done, the final commit tags a release. A reviewer should be able to clone the repo, run `pytest --cov=logalyzer` once, and see exactly what your contribution moved.

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Commit progress frequently as you go. Do not ask for clarification — make reasonable choices and document them in `/decisions/`.
