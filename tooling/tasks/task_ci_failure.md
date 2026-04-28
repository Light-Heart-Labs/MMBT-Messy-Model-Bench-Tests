You have access to a small Python project at `/input/repo/` whose CI is currently red. The full CI failure log is at `/input/repo/ci_failure.log`.

You have a fresh Linux VM with Python 3.11, standard CLI tools, and the project's dev toolchain (pytest, ruff). No time limit.

Your task: **make CI green.** Specifically, after your fixes:

1. `ruff check src/ tests/` must report zero errors.
2. `pytest -q` must pass all tests with exit code 0.

That's it. Two tools, both must be green.

## Constraints

- **Don't disable tests.** No `@pytest.mark.skip`, no deleting failing tests, no commenting them out. The test suite was right before someone made a change; either restore the function-under-test to its correct behavior, or fix the test if the test itself was wrong (use the changelog and code structure to decide which).
- **Don't suppress lint warnings.** No `# noqa`, no `[tool.ruff.lint.ignore]` additions. Fix the underlying issue.
- **Don't change the public API surface unless necessary.** The package's public exports are in `src/discountkit/__init__.py` and shouldn't change unless the CI failure specifically requires it.
- **Read the changelog.** It documents what changed between recent versions and what callers should expect.

## Output

Everything goes in a new git repository at `/workspace/`. Commit early, commit often. Each fix should be its own commit so a reviewer can follow the chain.

Required files:
- `/workspace/src/discountkit/` and `/workspace/tests/` — the fixed project (start by copying from `/input/repo/`)
- `/workspace/pyproject.toml` — copy from input, only modify if absolutely needed
- `/workspace/CHANGELOG.md` — extend with a v0.3.2 entry describing what you fixed
- `/workspace/diagnosis.md` — a brief writeup: for each failure, what was wrong and which way you decided to fix it (test vs code) and why
- `/workspace/decisions/` — ADR-style records for any non-obvious calls

## Verification — run these yourself before calling done()

From `/workspace/`:
1. `pip install -e ".[dev]"` (should already be set up by the harness)
2. `ruff check src/ tests/` → must exit 0 with no errors
3. `pytest -q` → must show "0 failed" and exit 0

Document the verification results in CHANGELOG.md.

When you're done, the final commit tags a release (v0.3.2 or similar).

Begin. Work autonomously. Use the bash, write_file, read_file, and done tools. Commit each fix as a separate commit. Do not ask for clarification — make reasonable choices and document them in `/workspace/decisions/` or `diagnosis.md`.
