# PR #1015 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(dashboard): template picker defensive fixes (handleApply + vacuous-truth)

## Author's stated motivation

The PR body says (paraphrased):

> ## ⚠️ Draft — depends on #1003 merging first

This PR is stacked on `fix/dashboard-setup-wizard` (#1003) because `lib/templates.js` (the target of the #409 fix) doesn't exist on `upstream/main` yet — it's created by #1003. Once #1003 merges, I'll rebase on `main` and the PR diff will collapse to exactly the 2-line change shown below under "Our delta".

## What
Two small defensive fixes in template-related dashboard code:

- **#409 — `lib/templates.js` `getTemplateStatus`**: add early-return `if (services.length === 0) return 'available'` guarding against `[].every(s => s === 'enabled')` returning true (vacuous truth). Without this, templates with `services: []` get misclassified as `'applied'` — silently hidden from the Extensions page (filter drops 'applied') and rendered as a disabled green "Applied" card in the setup wizard added by #1003.
- **#434 — `TemplatePicker.jsx` `handleApply`**: replace `const data = await res.json().catch(() => ({}))` with `const data = await res.json()`. The silent `.catch(() => ({}))` swallowed malformed server responses and fabricated an empty data object → UI showed a fake "already active" state. The outer `try/catch` at line 159 already sets `setError('Failed to apply template')` — letting parse errors bubble there gives users a visible error state.

## Our delta (post-#1003-rebase view)
Two files, two lines:
- `dashboard/src/lib/templates.js`: `+ if (services.length === 0) return 'available'`
- `dashboard/src/components/TemplatePicker.jsx`:  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
