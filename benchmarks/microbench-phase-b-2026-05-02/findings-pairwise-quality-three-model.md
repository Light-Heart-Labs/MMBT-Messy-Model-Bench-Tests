# 2026-05-03 — Three-model pairwise quality study (with correction to the 2026-04-28 study)

> Phase D of the post-audit follow-up. Extends the 2026-04-28 pairwise quality study (`27B-thinking vs Coder-Next`) to add 27B-no-think as a third arm on the both-ship microbench cells. Reads actual deliverables side-by-side rather than relying on the binary PASS/FAIL graders. Hand-graded; "claude-grading-claude" caveat applies.
>
> **Headline result**: 27B-thinking and 27B-no-think exhibit **identical** behavior on the load-bearing CHANGELOG-vs-test conflict on `p2_ci` — both correctly trust the documented v0.3.0 API change. Coder-Next regresses by trusting the test name over the docs. **The original 2026-04-28 study had this regression analysis reversed**; the correction is documented below.

## Why this matters

The microbench's binary PASS/FAIL graders pass all three models (typically 10/10 each at N=10) on the both-ship cells. But "all pass" doesn't mean "all equal." A model can pass `pytest` by changing the test to match a buggy implementation. A model can pass a JSON-schema check while losing nuance the schema doesn't capture. **Decisions about which local model to trust on real engineering work need quality data the binary graders don't provide.**

This study answers: when 27B-thinking, 27B-no-think, and Coder-Next all ship `done_signal` on the same task, are the deliverables actually equivalent?

## Method

For each of three both-ship cells, the v1 deliverables of all three models were extracted from `workspace_final.tar.gz` and read side-by-side. Cell-specific quality axes were defined a priori. Where the original 2026-04-28 study graded only 27B-thinking vs Coder-Next, this study adds 27B-no-think as a third arm using the same axes.

---

## Cell 1: CI failure debugging (`p2_ci`) — the load-bearing finding

**Task**: a Python project (`discountkit`) with three planted bugs causing ruff and pytest failures. Read the CI log, fix the bugs, ship a clean repo.

The three bug shapes:
1. Unused `import json` (ruff F401)
2. `discount_amount(price, percent_off)` returns `price * percent_off` not `price * percent_off / 100`
3. `Cart.line_count()` test asserts `== 5` (v0.2.0 behavior) but the prod code returns `len(self.lines)` (v0.3.0 behavior)

The CHANGELOG explicitly documents bug #3 as an intentional API change in v0.3.0:

> ## v0.3.0
>
> - `Cart.line_count()` now returns the number of lines, not the total quantity across lines. Tests should be updated where they relied on the old behavior.

The starter `tests/test_cart.py` retains the old v0.2.0 test (`assert c.line_count() == 5`); the prod code already implements the new v0.3.0 behavior (`return len(self.lines)`). **The correct fix is to update the test, not the prod code.**

### What each model did

| | 27B-thinking v1 | 27B-no-think v1 | Coder-Next v1 |
|---|---|---|---|
| `cart.py: line_count()` | Kept `return len(self.lines)` ✓ | Kept `return len(self.lines)` ✓ | Changed to `return sum(line.qty for line in self.lines)` ✗ |
| `tests/test_cart.py` | Updated to `assert c.line_count() == 2` ✓ | Updated to `assert c.line_count() == 2` ✓ | Kept `assert c.line_count() == 5` ✗ |
| Per CHANGELOG v0.3.0 contract | **Correct** | **Correct** | **Regression** (reverts to v0.2.0 behavior) |

### Both 27B variants reasoned correctly from the CHANGELOG

27B-thinking's `diagnosis.md` (excerpt):

> The v0.3.0 changelog explicitly states: "`Cart.line_count()` now returns the number of lines, not the total quantity across lines. Tests should be updated where they relied on the old behavior."
>
> The code correctly implements the documented behavior. The test was simply not updated when the API changed.

27B-no-think's `diagnosis.md` reaches the same conclusion via the same reasoning: trust the CHANGELOG over the stale test name.

### Coder-Next reasoned from the test name instead of the CHANGELOG

Coder-Next's `decisions/002-fix-line-count-implementation.md` (excerpt):

> However, the test `test_line_count_matches_qty_sum` clearly expects the total quantity. The test name "line_count_matches_qty_sum" explicitly states the expected behavior.
>
> **Test expectations should be trusted**: The test name "line_count_matches_qty_sum" explicitly states the expected behavior

This is the wrong heuristic for this task. The test name is a v0.2.0 artifact; the CHANGELOG explicitly says it's stale. Coder-Next's "trust the test" rule reverts the v0.3.0 API change.

### Why the binary grader passes both fixes

The grader's checks are: ruff exits 0, pytest exits 0, no `@pytest.mark.skip`, no `# noqa`, no suspicious `pyproject.toml` edits. Both fixes satisfy all of these. There's no per-task check for "did the fix preserve the documented v0.3.0 API contract?" — that requires task-specific knowledge that the generic grader doesn't have.

This is the canonical example of "binary grader passes but quality differs."

### Quality scoring (revised)

| Quality axis | 27B-thinking v1 | 27B-no-think v1 | Coder-Next v1 |
|---|:---:|:---:|:---:|
| Bug-fix correctness per documented API | **5/5** | **5/5** | 2/5 (reverts v0.3.0) |
| Diff scope (minimum-edit) | 4/5 | 4/5 | 4/5 |
| Diagnosis quality | 5/5 | 4/5 | 4/5 (well-written but reasons from the wrong source) |
| CHANGELOG quality | 4/5 | 4/5 | 3/5 (CHANGELOG-fix mismatch) |
| Type-annotation hygiene | 5/5 | 4/5 | 4/5 |
| **Average** | **4.6 / 5** | **4.2 / 5** | **3.4 / 5** |

**Blinded preference**: either 27B variant. Both 27B modes produce a fix that survives the v0.3.0 API contract; Coder-Next ships a regression that masquerades as a fix.

### Correction to the 2026-04-28 study

The original `findings/2026-04-28-pairwise-quality-study.md` § "Cell 2: CI failure debugging" reported this finding with the regression attributed to **27B**, not Coder-Next. That analysis read the CHANGELOG entry as documenting a change *toward* `total qty` — but the actual entry says *away from* `total qty`. The "v0.3.0 API per the documented changelog says line_count() should return total qty" claim in that study is reversed.

Re-reading the same starter CHANGELOG today, the v0.3.0 contract is unambiguous: **number of lines**, not total qty. 27B's fix matches; Coder-Next's reverts.

This correction strengthens the headline read of the prior study (binary graders miss real fix-quality differences) but reverses the model-attribution: it's Coder-Next's regression the grader misses, not 27B's. The findings doc tooling (graders, taxonomy, methodology) was correct; only the per-fix attribution was wrong.

The current PR's `tooling/scripts/check_substance.py` doesn't help here — substance-check catches scroll-loops in the transcript, not CHANGELOG-misreading regressions in the deliverable. Catching this requires either hand-grading or a per-task grader extension that compares the post-fix code to the documented API contract.

---

## Cell 2: structured extraction (`p2_extract`)

**Task**: read a Veridyne Networks Q3 FY2026 press release; produce JSON matching a 20-field schema with hedging-language disambiguation per field-specific rules.

**Programmatic verdict**: 27B-thinking 3/3 PASS at 100% accuracy on 20 fields; 27B-no-think 10/10 PASS; Coder-Next 3/3 PASS at ~92% accuracy. Numbers below are from v1 specifically.

### Findings

| Quality axis | 27B-thinking v1 | 27B-no-think v1 | Coder-Next v1 |
|---|:---:|:---:|:---:|
| Field accuracy on 20-field schema | 5/5 (20/20) | 5/5 (20/20) | 4/5 (~18-19/20) |
| Hedging-language disambiguation | 4/5 | 4/5 | 4/5 |
| Format compliance | 5/5 | 5/5 | 5/5 |
| Reasoning documentation | 5/5 (dense inline) | 4/5 (terse — no separate ADR docs) | 4/5 (4 separate ADRs) |
| Edge cases | 4/5 | 4/5 | 4/5 |
| **Average** | **4.6 / 5** | **4.4 / 5** | **4.2 / 5** |

**Difference between 27B-thinking and 27B-no-think on this cell**: thinking-mode produces the same output content but with denser inline reasoning notes (per-field provenance comments inside the JSON's `notes` array). No-think produces the same JSON correctness with sparser commentary. For downstream JSON consumers, the outputs are interchangeable. For human readers tracing reasoning, thinking-mode gives more breadcrumbs.

**No-think is not a regression on this cell** — accuracy is preserved; only the meta-commentary is thinner. This is consistent with the no-think trade-off observed on `p3_doc`: faster, leaner output, slightly less polished prose, but the substantive deliverable is intact.

---

## Cell 3: customer support triage (`p2_triage`)

**Task**: closed-vocabulary classification + duplicate-cluster recall. Both models 3/3 (and 10/10 for no-think) PASS the binary grader.

The original 2026-04-28 study identified an "urgency-calibration gap" between 27B-thinking and Coder-Next on this cell. With no-think added, the question is: is no-think more like thinking-mode 27B or like Coder-Next on urgency calibration?

### Quick read of v1 outputs

- 27B-thinking v1: 86.7% category accuracy, 100% duplicate-cluster recall. Urgency labels reasoned per-ticket with explicit risk justification.
- 27B-no-think v1: 86.7% category accuracy (same — both 27B modes class-perfect on 13/15 same items), 100% duplicate-cluster recall. Urgency labels assigned with brief justification (less verbose than thinking-mode).
- Coder-Next v1: 96.7% category accuracy (slightly higher), 100% duplicate-cluster recall. Urgency labels assigned with minimal justification.

**No-think is again interchangeable with thinking-mode on the substantive output**; only the verbosity of justification differs. The "urgency-calibration gap" between 27B-family and Coder-Next persists; no-think aligns with thinking-mode here, not with Coder-Next.

---

## Headline reads of this study

### Three-model picture

1. **27B-thinking and 27B-no-think are tightly correlated** on the both-ship cells. Where they make decisions (CHANGELOG interpretation, urgency calibration, hedging language), they make the same decisions. The difference is in the volume and density of reasoning prose, not the substantive output. **For decision-making, they can be treated as one "27B model" with a thinking-mode flag for prose-density.**

2. **Coder-Next has a distinct reasoning style**: trust artifact-local signals (test names, structural hints) over external documentation. This is a strength on tasks where the test/code IS the spec, and a weakness on tasks where the spec lives in a CHANGELOG / API contract / external doc.

3. **The binary graders miss real fix-quality differences** in the way the original 2026-04-28 study identified — but the model-attribution of *which* model regresses on `p2_ci` was wrong. The corrected reading: **Coder-Next regresses, both 27B variants do the right thing.** The grader misses Coder-Next's regression, not 27B's.

### Decision implications

- **For tasks with CHANGELOG / API-contract / external-spec resolution**: prefer 27B (either mode). It reads the docs.
- **For tasks where the test/code IS the spec and there's no external authority**: Coder-Next is fine and ~5-10× faster.
- **For tasks where you want dense provenance/reasoning prose alongside the deliverable**: prefer 27B-thinking. For lean output of the same correctness: 27B-no-think.

## Caveats

- **Hand-graded; claude-grading-claude.** The grader (Claude Opus 4.7) is a different model from the gradees (the three Qwen3 quants) and the analysis is grounded in specific quoted differences. But a human pass would be the next step if these findings load-bear for a deployment decision.
- **N=1 per (model × cell).** Only the v1 deliverables were read side-by-side. With N=10 available per cell for 27B-no-think and N=3-10 for the others, reading additional Vs would tighten the picture (especially on `p2_ci` where the CHANGELOG-vs-test conflict either reproduces across all 10 27B-no-think runs or doesn't).
- **The 2026-04-28 study correction applies only to `p2_ci`.** The methodology, axes, and grader-extension recommendations from that study still stand; only the per-fix attribution on this one cell is reversed.
- **The original test name (`test_line_count_matches_qty_sum`) is itself misleading** — it asserts a v0.2.0 contract under a name that survives into v0.3.x. A grader extension could flag tests where the name and the post-CHANGELOG-update assertion conflict.
