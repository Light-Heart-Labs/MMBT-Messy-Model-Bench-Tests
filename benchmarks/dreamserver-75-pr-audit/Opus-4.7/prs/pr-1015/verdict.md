# PR #1015 — Verdict

> **Title:** fix(dashboard): template picker defensive fixes (handleApply + vacuous-truth)
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `fix/dashboard-template-picker-defensive`
> **Diff:** +217 / -58 across 6 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1015

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **4** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**HOLD — depends on #1003 landing first.** The PR body claims a 2-line delta
(early-return for empty `services` in `getTemplateStatus`, removal of a
silent `.catch(() => ({}))` in `TemplatePicker.handleApply`), but the actual
diff is +217/-58 across 6 files because it's stacked on the unmerged #1003
setup-wizard PR. The current diff includes the entire setup-wizard backend
sentinel emitter, the `lib/templates.js` extraction, and full
`SetupWizard.jsx` refactor — all of which belong to #1003. Once #1003 lands
the post-rebase delta will be exactly the two defensive fixes claimed, both
of which are correct.

## Findings

- The genuine fix is right. `[].every(s => s === 'enabled')` returns vacuous
  true; an empty-services template was being misclassified as `'applied'`,
  silently hidden from Extensions and rendered as a disabled green card in
  the wizard. Early-return on `services.length === 0` is the minimal correct
  fix.
- The `.catch(() => ({}))` removal in `TemplatePicker.handleApply` is the
  right call. The outer `try/catch` at line 159 already calls
  `setError('Failed to apply template')`, so swallowing parse errors with an
  empty `data` object only created a bogus "already active" UI state.
- The PR body explicitly flags this as draft pending #1003 and projects
  the post-rebase diff. Correctly self-aware.
- Per the setup-wizard cluster recommendation in `dependency-graph.md`, this
  should ship in the same merge train as #1003, #1018, and #1019. They are
  one logical unit.

## Cross-PR interaction

- Hard dependency on #1003 (verdict already MERGE-first per cluster guidance).
- Stacked alongside #1018 (BATS coverage), #1019 (sentinel exception path).
  All three drafts depend on #1003.
- No overlap with non-cluster PRs.

## Trace

- `dream-server/extensions/services/dashboard/src/lib/templates.js:14`
  (post-rebase) — early-return for empty services
- `dream-server/extensions/services/dashboard/src/components/TemplatePicker.jsx:152`
  (post-rebase) — `.catch(() => ({}))` removed
- `dream-server/extensions/services/dashboard/src/components/TemplatePicker.jsx:159`
  — outer try/catch that already surfaces errors (relied on by the fix)
- See `analysis/dependency-graph.md` Cluster 4 for the setup-wizard merge
  train ordering
