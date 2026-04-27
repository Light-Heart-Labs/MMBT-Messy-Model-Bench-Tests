# PR #1019 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> test+fix(setup): complete __DREAM_RESULT__ sentinel contract (exception path + tests)

## Author's stated motivation

The PR body says (paraphrased):

> ## ⚠️ Draft — depends on #1003 merging first

#1003 (`fix/dashboard-setup-wizard`) introduces the `__DREAM_RESULT__:PASS|FAIL:<rc>` sentinel parser in `SetupWizard.jsx` and the emitter for the happy-path + error-stream branches. This PR completes the contract by adding the emitter for the **exception path** (previously the generator could raise mid-stream without ever yielding a sentinel) plus full test coverage for all three branches.

Once #1003 merges, rebase drops the merge commit and the PR diff reduces to: `routers/setup.py` (+14 / -1) + 3 new test files.

## What

### Backend — `routers/setup.py` exception-path sentinel
Wraps the `run_setup_diagnostics` generator body in try/except. **Re-raises `CancelledError` and `OSError`** (transport-level concerns — client disconnect, broken pipe — should propagate normally). Catches generic `Exception`, logs with `logger.exception()`, yields a `FAIL:1` sentinel so the frontend parser never gets stuck in partial-state UI.

The `except Exception` is tagged `# noqa: BLE001 — sentinel contract requires *some* terminal signal`. CG reviewed and accepted this as a CLAUDE.md §2 I/O-boundary exception — narrow, logged, and the wire contract with the React parser is explicit.

### Tests (3 new files, 18 assertions)
- **pytest — `test_setup_sentinel.py`** (5 cases): asserts PASS:0 on success, FAIL:`<rc>` on non-zero exit, fallback sentinel when script missing, machine-parseable regex format, auth required. 5/5 pass locally.
- **Vitest — `Se  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
