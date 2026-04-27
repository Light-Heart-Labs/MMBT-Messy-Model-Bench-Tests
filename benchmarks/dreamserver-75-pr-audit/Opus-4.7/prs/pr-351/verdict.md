# PR #351 — Verdict

> **Title:** test: add comprehensive input validation and injection resistance tests
> **Author:** [reo0603](https://github.com/reo0603) · **Draft:** False · **Base:** `main`  ←  **Head:** `feat/input-validation-test-suite`
> **Diff:** +370 / -2 across 5 file(s) · **Risk tier: Low (score 6/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/351

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 3 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 3 | _see review.md_ |
| **Total** | **6** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**REJECT — quality.** This is the older of the two CONFLICTING March-era PRs. The diff is structurally broken: an unresolved git conflict marker (`>>>>>>> 8a44877 (test: add comprehensive...)`) is committed at `dashboard-api/tests/test_routers.py:111`, which means the file is unparseable Python on merge. The PR also misrepresents itself: the description claims "test-only with zero production code changes," but the diff modifies `dashboard-api/models.py:5-25` (adds a `validator` import + `validate_port_range` validator) and `dashboard-api/routers/workflows.py:250-275` (adds three regex `re.match` rejecters that 400-error any non-`[a-zA-Z0-9_-]+` workflow ID). Those are functional changes, not tests.

## Findings

- **Unresolved conflict marker in committed code.** `dashboard-api/tests/test_routers.py` ends with `>>>>>>> 8a44877 (test: add comprehensive input validation and injection resistance tests)` on its final line. This alone makes the PR unmergeable — pytest collection would syntax-error before any test runs. CONFLICTING status from the GitHub merge metadata (`mergeStateStatus: DIRTY`) is consistent with this.
- **Body misrepresents scope.** The description (and PR title) say "test-only," but `models.py` and `routers/workflows.py` get production-code edits. Even if those edits are reasonable (port range 1–65535, alphanumeric workflow ID), they need to be reviewed as production changes, not landed under a test PR. They were almost certainly already addressed by the merged security-hardening commits the body cites (`ce53ae6`, `686f284`, `a83dbec`) — that's why the PR is now stale.
- **Pydantic v1 `@validator` syntax.** `validator('ports', each_item=True)` in `models.py` is the v1 API (deprecated in pydantic v2). Anywhere else in the codebase using v2 `field_validator` would conflict. Even if accepted, this would need a syntax update.

## Cross-PR interaction

- This PR's `routers/workflows.py` edit overlaps with anything else touching that file post-March; per `analysis/dependency-graph.md` Cluster 3 (8 PRs touching `dashboard-api/routers/extensions.py`), the dashboard-api surface has been heavily revised.
- No semantic conflict with the open set; the work is superseded.

**Recommendation for Michael:** Close with a short note thanking the contributor and pointing them at the security hardening commits that already shipped. Or: ask reo0603 if they want to extract just the *test additions* (the new `test_security_validation.py` file and the workflow ID test additions) into a fresh PR rebased on `main`. The conflict marker has to go either way.

## Trace

- `dream-server/extensions/services/dashboard-api/tests/test_routers.py:111` — committed `>>>>>>> 8a44877` conflict marker.
- `dream-server/extensions/services/dashboard-api/models.py:5-25` — undeclared production change (port validator).
- `dream-server/extensions/services/dashboard-api/routers/workflows.py:253, 261, 270` — undeclared production change (regex 400-on-bad-ID).
- `meta.json: mergeStateStatus = "DIRTY", mergeable = "CONFLICTING"`, `updatedAt = 2026-04-18` (last touched 9 days ago, original 2026-03-17).
