# PR #1019 — Verdict

> **Title:** test+fix(setup): complete __DREAM_RESULT__ sentinel contract (exception path + tests)
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `test/setup-wizard-template-picker-coverage`
> **Diff:** +689 / -60 across 9 file(s) · **Risk tier: Trivial (score 3/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1019

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **3** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — depends on #1003 landing first.** The PR body claims a
`routers/setup.py` (+14/-1) change plus three new test files; the actual
+689/-60 diff is inflated because it carries the entire #1003 setup-wizard
sentinel emitter, the `lib/templates.js` extraction, and the
`SetupWizard.jsx` refactor. Post-#1003 rebase, the genuine delta is the
exception-path try/except in `routers/setup.py:154-176` plus
`test_setup_sentinel.py` (5 pytest cases), `SetupWizard.test.jsx`
(6 vitest cases), and `TemplatePicker.a11y.test.jsx` (7 vitest cases).
The `except Exception` is narrowly scoped (re-raises `CancelledError` and
`OSError`, logs via `logger.exception`, yields `FAIL:1` sentinel) and is the
correct CLAUDE.md §2 I/O-boundary carve-out — without it, the React parser
gets stuck in partial-state UI when the generator raises.

## Findings

- The exception-path design is right. Re-raising `CancelledError` is required
  (it must propagate so the runtime can finalize the task tree); re-raising
  `OSError` is right (transport-level, client gone). The bare
  `except Exception` is exactly the kind of narrow boundary catch the project
  rules carve out — logged, scoped to one generator, with an explicit wire
  contract to the React parser. The `# noqa: BLE001` annotation makes intent
  inspectable.
- The PR body honestly admits the exception-path yield isn't directly
  exercised by the 5 pytest cases (would require monkeypatching
  `asyncio.create_subprocess_exec` to raise). Worth filing as a follow-up,
  not blocking.
- `TemplatePicker.a11y.test.jsx` bulk-asserts `aria-hidden="true"` on all
  SVGs, which the body identifies as fragile if a future PR adds a
  semantically-meaningful SVG. Reasonable trade-off for now.
- Vitest tests weren't run locally (no `npm install` in the worktree); CI will
  exercise them. Manageable.

## Cross-PR interaction

- Hard dependency on #1003. Per `dependency-graph.md` Cluster 4, this PR
  ships in the same merge train as #1003, #1015, #1018.
- No overlap with non-cluster PRs.

## Trace

- `dream-server/extensions/services/dashboard-api/routers/setup.py:154-176`
  (post-rebase) — exception-path try/except + sentinel yield
- `dream-server/extensions/services/dashboard-api/tests/test_setup_sentinel.py`
  — new pytest file (5 cases)
- `dream-server/extensions/services/dashboard/src/components/__tests__/SetupWizard.test.jsx`
  — new vitest file (6 cases)
- `dream-server/extensions/services/dashboard/src/components/__tests__/TemplatePicker.a11y.test.jsx`
  — new vitest file (7 cases)
- `dream-server/extensions/services/dashboard/src/components/SetupWizard.jsx:104`
  — frontend parser regex the sentinel format must match
