# DreamServer 75 PR Audit - GPT-5.5

This folder is GPT-5.5's entry for the DreamServer 75-PR messy benchmark.

## Read In This Order

1. `report/executive-summary.md`
2. `report/backlog-strategy.md`
3. `analysis/dependency-graph.md`
4. `analysis/risk-matrix.md`
5. `prs/pr-*/verdict.md` for PR-level decisions
6. `ACTIONABLE_FINDINGS_INDEX.md` for line-level issues

## Folder Layout

- `report/` contains maintainer-facing synthesis.
- `prs/pr-{number}/` contains per-PR verdicts, summaries, review notes, tests,
  diff analysis, interactions, and trace records.
- `testing/` contains baseline, environment notes, hardware notes, and
  reproduction pointers.
- `analysis/` contains cross-PR dependency, risk, surface-area, and script
  artifacts.
- `research/` contains upstream context, questions, dead ends, and dated working
  notes.
- `decisions/` contains ADR-style records for audit methodology choices.

## Final Accounting

- Total PRs audited: 75
- Merge: 34
- Revise: 40
- Reject: 1
- Unaudited: 0

The "Merge" set assumes normal CI, maintainer review, and the merge ordering
recommended in `report/backlog-strategy.md`.

## Verification

Run from this folder:

```bash
python analysis/scripts/verify_coverage.py
```

Expected result:

```text
coverage check passed: 75 PRs, 7 required artifacts each
```
