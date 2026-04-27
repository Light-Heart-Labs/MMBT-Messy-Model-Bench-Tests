# PR #1014 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> fix(tests): repair extension summary assertion in doctor diagnostics test

## Author's stated motivation

The PR body says (paraphrased):

> ## What
Replaces the order-dependent regex in `tests/test-doctor-extension-diagnostics.sh` test #9 ("Extension summary output present") with two order-independent chained greps.

## Why
The existing assertion
```bash
grep -q "ext_total.*ext_healthy" "$ROOT_DIR/scripts/dream-doctor.sh"
```
requires `ext_total` to appear **first** on the matched line. But `scripts/dream-doctor.sh:364` emits
```python
print(f"  Extensions:    {ext_healthy}/{ext_total} healthy, {ext_issues} with issues")
```
— `ext_healthy` comes first. The grep has been permanently failing since the format was introduced; test #9 has been broken on every branch that inherits from `main`.

## How
Switches to the chained-grep idiom already used elsewhere in the same file (test #7, lines 74–80, which checks for `extensions_total`, `extensions_healthy`, and `extensions_issues`):
```bash
if grep -q "ext_total" "$ROOT_DIR/scripts/dream-doctor.sh" && \
   grep -q "ext_healthy" "$ROOT_DIR/scripts/dream-doctor.sh"; then
```
Order-independent and future-proof against either variable being reordered in the print statement.

## Testing
- [x] `bash -n tests/test-doctor-extension-diagnostics.sh` — clean
- [x] `shellcheck tests/test-doctor-extension-diagnostics.sh` — no new warnings
- [x] `bash tests/test-doctor-extension-diagnostics.sh` — all 9 tests pass (was 8/9 before this change)
- [x] Pre-commit (gitleaks / private-key / large-file) — clean

## Platform Impact
- **macOS**: passes
- **Linux**: passes (CI runs on Ubuntu —   …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
