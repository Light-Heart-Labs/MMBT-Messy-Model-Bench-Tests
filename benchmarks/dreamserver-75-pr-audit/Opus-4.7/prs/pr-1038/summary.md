# PR #1038 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard-api): honor pre_start return, surface post_start failure

## Author's stated motivation

The PR body says (paraphrased):

> > **DRAFT: must merge AFTER #1031.** This branch is based on `fix/progress-state-machine` (#1031) and depends on `_write_error_progress` introduced there. Promote to ready-for-review after #1031 merges.

## Summary
`enable_extension` silently discarded the return value of `_call_agent_hook("pre_start")` and only logged `post_start` failures at WARN. Extensions with failing hooks could appear healthy while actually misconfigured.

## How
- **`pre_start` failure** now skips `_call_agent("start", ...)`, sets `agent_ok=False`, and writes an error progress entry via `_write_error_progress` so the UI card shows an error badge with `pre_start hook failed — extension not started.` instead of a stuck "installing" state.
- **`post_start` failure** appends `f"{svc_id}: post_start hook failed — manual configuration may be needed"` to a new `warnings: list[str]` in the response. `agent_ok` is NOT flipped — the service is running; consumers can surface the warning as a non-fatal notice.
- `warnings` is always present in the response (possibly empty) so frontend iteration is trivial.

## Platform Impact
- **macOS / Linux / Windows-WSL2**: identical. Python inside the dashboard-api container.

## Testing
- `pytest tests/test_extensions.py tests/test_extensions_deps.py tests/test_templates.py` → 168 passed.
- ruff clean on the two touched files.
- 3 new tests (`TestEnableExtensionHookReturnHandling`): pre_start-fail blocks start, post_start-fail returns warning, both-succeed baseline.

Manual  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
