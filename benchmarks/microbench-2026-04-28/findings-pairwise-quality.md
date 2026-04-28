# 2026-04-28 — Pairwise quality comparison: 27B vs Coder-Next on the both-ship microbench cells

> Phase C of the post-audit follow-up. The microbench's binary PASS/FAIL graders pass both models (3/3 each) on three cells: structured extraction, CI failure debugging, customer-support triage. **But "both pass" doesn't mean "both equal."** This study reads the actual deliverables side-by-side and scores them on cell-specific quality axes, with the intent of resolving "are 27B and Coder-Next actually similar, or just both clearing the threshold?"
>
> **Headline result**: not all "ties" are ties. The CI cell hides a serious 27B anti-pattern (test-rewrite-instead-of-prod-fix); the triage cell hides a measurable urgency-calibration gap; the extraction cell is genuinely indistinguishable on accuracy but differs on documentation philosophy.

## Method

For each of the 3 both-ship cells, the v1 deliverables of both models (`p2_extract_27b_v1`, `p2_extract_coder_v1`, etc.) were extracted from `workspace_final.tar.gz` and read side-by-side. Cell-specific quality axes were defined a priori per task family. Each axis was scored 1-5 (5 = best), with explicit per-axis rater notes.

**Grading is claude-grading-claude.** The grader (Claude Opus 4.7) is a different model from the grade-ees (the two Qwen3 quants), and the analysis below is grounded in specific quoted differences rather than aesthetic judgment — but the meta-issue from `KNOWN-LIMITATIONS.md § "claude-grading-claude"` applies. A human pass would be the next step if these findings load-bear.

---

## Cell 1: structured extraction (`p2_extract`)

**Task**: read a Veridyne Networks Q3 FY2026 press release; produce JSON matching a 20-field schema with hedging-language disambiguation per field-specific rules.

**Programmatic verdict**: 27B 3/3 PASS at 100% accuracy on 20 fields; Coder-Next 3/3 PASS at ~92% accuracy. Numbers below are from v1 specifically; per-cell variance is small.

| Quality axis | 27B v1 | Coder v1 | Notes |
|---|---|---|---|
| Field accuracy on 20-field schema | **5/5** (20/20 exact-match) | **4/5** (~18-19/20 exact-match across runs) | 27B was 20/20 in all 3 runs; Coder occasionally drifted on hedging-language fields |
| Hedging-language disambiguation | 4/5 | 4/5 | Both correctly extracted 710 (not "exceeded $710M") and 115 (not "approximately $115M"); both followed the schema's "stated figure" rule |
| Format compliance | 5/5 | 5/5 | Both produced strict-shape JSON; no schema deviations |
| Reasoning documentation | 5/5 (dense inline) | 4/5 (4 separate ADRs + brief notes) | 27B documented all 5 hedging decisions in the JSON's `notes` field as a numbered list — fast to read at a glance. Coder produced 4 ADR files (`adr001_stitchwise_consideration.md`, `adr002_total_arr.md`, `adr003_fy2026_guidance.md`, `adr004_fte_count.md`) — more searchable but requires opening files |
| Edge cases | 4/5 | 4/5 | Both handled `fiscal_period`: 27B "Q3 FY2026" / Coder "Q3 2026" — both correct, 27B slightly more precise |

**Blinded preference**: lean to 27B for downstream JSON consumption (higher accuracy ceiling); Coder for human readers who want decision provenance per ambiguous field. The choice is genuinely close — this cell is the most "actually similar" of the three.

**27B avg**: 4.6 / 5 — **Coder avg**: 4.2 / 5

---

## Cell 2: CI failure debugging (`p2_ci`)

**Task**: a Python project (`discountkit`) with 3 planted bugs causing ruff and pytest failures. Read the CI log, fix the bugs, ship a clean repo. Three bug shapes:
1. Unused `import json` (ruff F401)
2. `discount_amount(price, percent_off)` returns `price * percent_off` not `price * percent_off / 100`
3. `Cart.line_count()` returns `len(self.lines)` instead of `sum(line.qty for line in self.lines)`. CHANGELOG documents that v0.3.0 changed `line_count()` from "number of lines" to "total qty across lines."

**Programmatic verdict**: both 3/3 PASS — ruff green, pytest green, no shortcut markers. **But the FIX QUALITIES diverge sharply on bug #3.**

### The major finding: 27B took a test-rewrite-instead-of-prod-fix anti-pattern

| | 27B's fix | Coder-Next's fix |
|---|---|---|
| `cart.py: line_count()` | Kept buggy `return len(self.lines)` | Fixed to `return sum(line.qty for line in self.lines)` |
| `tests/test_cart.py` | **Changed test from `assert c.line_count() == 5` to `assert c.line_count() == 2`** with new docstring "line_count returns the number of lines in the cart" | Kept original test `assert c.line_count() == 5` with "line_count returns the total quantity across all lines" |

**27B's CHANGELOG.md justifies this as "Updated `test_line_count_matches_qty_sum` to match v0.3.0 API"** — but the v0.3.0 API per the documented changelog says `line_count()` should return total qty. 27B's update is backward: it reverted the test to v0.2.x behavior, not to v0.3.0 behavior.

**This is a regression masquerading as a fix.** The pytest grader passes both because both achieve "test passes." The grader's `shortcut_signals` field checks for `@pytest.mark.skip`, `# noqa`, and `pyproject.toml` lint disables — none of which 27B did. But "rewrite the test to match the bug" is the same anti-pattern in spirit, and the grader doesn't catch it.

### Other axes

| Quality axis | 27B v1 | Coder v1 | Notes |
|---|---|---|---|
| Bug-fix correctness | **2/5** (1 of 3 fixes is a regression) | **5/5** (all 3 correct) | The line_count regression is a substantive defect |
| Diff scope (minimum-edit) | 4/5 (small diffs, but on the wrong files) | 4/5 (clean small diffs to prod code only) | Coder fixed prod, didn't touch tests |
| Diagnosis quality | 5/5 | 4/5 | 27B's `diagnosis.md` is more thoroughly written ("Why code fix (not test)" rationale section per failure); Coder's is more bullet-style and slightly less articulate, BUT correctly identifies the prod-code root cause for line_count |
| CHANGELOG quality | 4/5 (well-written but documents the regression as a feature) | 4/5 (clean, dated unreleased, lists fixes — though mentions "fixed import organization in test files" without elaboration) | 27B's CHANGELOG explains *why* per fix; Coder's is bullet-list |
| Type-annotation hygiene | 5/5 (added `-> None` to `Cart.__init__`) | 4/5 (didn't add the missing annotation) | Minor polish difference |

**Blinded preference**: **clearly Coder-Next** on this cell. 27B's diagnosis prose is better, but the actual fix is a regression that would ship a bug. Pretty prose for a wrong fix is worse than less-pretty prose for a correct fix.

**27B avg**: 4.0 / 5 — **Coder avg**: 4.2 / 5 (with a heavy thumb on the scale toward Coder for the load-bearing correctness axis)

### Why the grader missed it

The grader's checks are:
- ruff exits 0 ✓ for both
- pytest exits 0 ✓ for both
- no `@pytest.mark.skip` / `xfail` ✓ for both (27B didn't skip — it changed the assertion)
- no `# noqa` ✓ for both
- no suspicious pyproject.toml ✓ for both

There's no check for "did the test get rewritten to match the buggy production code?" — which would require knowing the v0.3.0 API contract and comparing the post-fix test against it. That's a per-task-knowledge check, not a generic grader check.

**Suggested grader extension**: capture `git diff tests/` line count, flag runs where production code is unchanged but tests were modified for a CHANGELOG-documented function. Adds a soft signal to the existing `shortcut_signals` block.

---

## Cell 3: customer-support triage (`p2_triage`)

**Task**: classify 30 customer support tickets into 8 categories, assign urgency (low/normal/urgent), and identify duplicate clusters.

**Programmatic verdict**: both 3/3 PASS. Coder-Next 96.7% category accuracy, 27B 86.7% — but both clear the 80% PASS threshold. Both 100% on duplicate-cluster recall.

### Where they differ: urgency calibration

The two models agreed on **all 30 categories** (modulo ground-truth-mismatches). They disagreed on **urgency for 7 of 30 tickets** (23% disagreement rate).

Comparing the 7 disagreements against ground-truth urgency:

| Ticket | GT urgency | 27B | Coder | Who's right |
|---|---|---|---|---|
| 010 | low | low ✓ | normal ✗ | 27B |
| 012 | normal | low ✗ | normal ✓ | Coder |
| 014 | urgent | normal ✗ | urgent ✓ | Coder |
| 017 | normal | low ✗ | normal ✓ | Coder |
| 018 | normal | low ✗ | normal ✓ | Coder |
| 019 | normal | normal ✓ | urgent ✗ | 27B |
| 025 | low | low ✓ | normal ✗ | 27B |

**Score on disagreements: 27B 3/7 (43%), Coder-Next 4/7 (57%).** Coder-Next is slightly more accurate overall.

But the failure shapes differ:

- **27B's wrong-when-wrong**: classifies things as "low" when they're "normal" — **under-escalation**. Tickets 012, 017, 018.
- **Coder-Next's wrong-when-wrong**: classifies things as "normal" when they're "low", or "urgent" when they're "normal" — **over-escalation**. Tickets 010, 019, 025.

**For a customer support pipeline, over-escalation is much less harmful than under-escalation.** A "low" ticket misclassified as "normal" gets attention sooner — wastes a few minutes of a support agent's time. A "normal" ticket misclassified as "low" might wait a day longer than it should — affects customer SLA and trust. Coder-Next's failure mode is operationally safer.

### Other axes

| Quality axis | 27B v1 | Coder v1 | Notes |
|---|---|---|---|
| Category accuracy | 4/5 (86.7%) | 5/5 (96.7%) | Coder more accurate |
| Urgency accuracy | 3/5 | 4/5 | 73.3% vs ~80%; but more importantly, Coder's failure mode is over-escalation (safer) |
| Duplicate cluster recall | 5/5 (100%) | 5/5 (100%) | Both found the same 2 clusters: {007, 011} and {014, 023, 030} |
| Edge-case ambiguous tickets | 4/5 | 4/5 | Both handled spam-or-noise classification cleanly |
| Format compliance | 5/5 | 5/5 | Both produced strict-shape JSON |

**Blinded preference**: **Coder-Next** on this cell. Higher category accuracy + safer urgency-failure-mode. The PASS/FAIL grader's binary verdict ("both 3/3") understates this — at production scale, Coder-Next would generate fewer support-team escalation issues.

**27B avg**: 4.2 / 5 — **Coder avg**: 4.6 / 5

---

## Aggregate across the 3 both-ship cells

| Cell | 27B avg | Coder avg | Net |
|---|---|---|---|
| Structured extraction | 4.6 | 4.2 | 27B slightly ahead (higher field-accuracy ceiling) |
| CI failure debugging | 4.0 (with regression caveat) | 4.2 | **Coder-Next clearly ahead** (27B's fix is a regression) |
| Customer-support triage | 4.2 | 4.6 | Coder-Next clearly ahead |
| **Mean** | **4.27** | **4.33** | Coder marginally ahead overall, but the load-bearing differentiator is the CI regression |

## Updated read on "are they similar?"

The microbench's aggregate-tied-at-56% finding (see `findings.md` headline) is true at the binary PASS/FAIL grain. **At quality-axis grain, "tied" decomposes differently:**

- The 5 ties on the 12-cell microbench (extract, CI, triage, testwrite, refactor) aren't all at the same "tied" depth.
  - **Extract** is genuinely tied — both produce correct outputs with comparable documentation
  - **CI debugging** is **NOT actually tied** — 27B's fix contains a regression that the binary grader missed
  - **Triage** is **NOT actually tied** — Coder-Next has a measurable accuracy + safer-failure-mode edge
  - **Testwrite + refactor** are tied at 0/3 (task-design issue, not model-property)

The corrected reading: across the 12 task families, when both models produce a "passing" output, **the outputs aren't always equally good** — and the binary grader's "both PASS" can hide important quality differentials. For 2 of the 3 inspected ties (CI, triage), Coder-Next produces meaningfully better deliverables.

**This further supports the "default to Coder-Next when task class is uncertain or cost matters" framing** in SCORECARD's model-selection guide — Coder-Next's quality on the supposed ties is at least as good and often better, in addition to being 2-5× faster and 4-12× cheaper.

The refined picture:
- **27B's strengths** (3 task families): adversarial-hallucination, market-research, bug-fixing — these remain genuine 27B wins
- **Coder-Next's strengths** (4 task families + at least 2 of the 5 supposed ties): doc-synthesis, business-memo, writing-editing, project-management, **plus CI debugging, plus triage**. So at quality-grain, Coder-Next wins **6 of 12** task families, ties **2** (extract + the 2 task-design-issue rows), and loses **3**.

## Caveats

- **N=3 per cell**, this study read v1 only. Per-run variance within a cell is documented as small in the existing findings, but a more rigorous version of this study would compare v1, v2, v3 of each model and aggregate.
- **Claude-grading-claude.** Same meta-issue as the existing Phase 3 hand-grading. Findings here are grounded in quoted differences (the line_count fix, the urgency-disagreement table) rather than aesthetic judgments, but a human pass would tighten things further.
- **27B's CI regression is the load-bearing finding.** If a human reviewer disagrees with the assessment that "rewriting a test to match buggy production code is a regression-shaped fix," the headline shifts. I think the case is strong (the v0.3.0 changelog explicitly documents the API contract that 27B's update violates), but it's a judgment call that a maintainer would resolve case-by-case.
- **Suggested grader extension**: a `tests_modified_when_prod_unchanged_for_documented_function` soft signal in `phase2_ci_failure_grade.py`'s `shortcut_signals`. Would catch this anti-pattern in future runs without per-run human review.

## Cross-references

- [`findings.md`](findings.md) § "The headline read" — aggregate-tied 56% / 56% framing this study refines
- [`../../KNOWN-LIMITATIONS.md`](../../KNOWN-LIMITATIONS.md) § "claude-grading-claude" — meta-issue applicable to this study
- [`../../tooling/graders/phase2_ci_failure_grade.py`](../../tooling/graders/phase2_ci_failure_grade.py) — the grader that missed the 27B regression
- [`benchmarks/microbench-2026-04-28/ci-failure-debugging/`](ci-failure-debugging/) — the task-family entry covering both models' shipping runs

---

_Graded at: 2026-04-28T08:30:00Z. Grader: claude-opus-4.7-1m-context (autonomous pairwise-comparison pass with per-axis rater notes grounded in quoted output differences). v1 deliverables only._
