# Unattended publish-path hardening — bench_report.py / bench_autopilot.py

Date: 2026-05-30. Audited against the LIVE N=20 run (autopilot pid 2646444, no-think
arm in flight, ~166/480 cells) WITHOUT disturbing it: no `--once`, no status.json
write, no autopilot invocation. Pure read-only log inspection + read-only import of
the autopilot's `arm_progress` for the scorecard cross-check.

## What I verified (and it checked out)

1. **Scorecard pass/N vs hand recount of grade.json** — `bench_report.py --n 20`
   and `--n 10` scorecard cells match a direct recount for every spot-checked
   task/arm: p1_bugfix nothink 5/5, p1_bugfix think 3/3, p3_market nothink 8/10,
   p3_market think 3/3, p3_pm nothink 5/10, p3_pm think 0/3, p3_doc think 1/3,
   p1_testwrite nothink 0/10, p1_refactor think 0/3. Totals: nothink **77/115**,
   think **22/36**. Pass = PASS|STRUCTURAL_PASS, ungraded excluded from denominator
   — as documented. Independent global tally: 88 PASS + 11 STRUCTURAL_PASS = 99
   passes = 77 (nothink) + 22 (think). Consistent.

2. **finish_reason audit (Section 4) self-consistency** — recount matches exactly:
   nothink 114 done_signal / 3 model_stopped / 2 stuck = 119 cells, 5 non-clean;
   think 47 done_signal, 0 non-clean. The five non-clean cells are named correctly.
   No GRADER_FAILED / MISSING_OUTPUT verdicts exist anywhere, so the autopilot
   harness-anomaly alert is not mis-firing.

3. **Redistribution table** — common-window math is correct: per-task k =
   min(nothink graded, think graded); Δcount = think_pass − nothink_pass over the
   same k. Spot-checked p3_market (+2), p3_pm (−2), p3_doc (−1); aggregate "helps 1,
   hurts 2, net −1" matches the published N=3 narrative direction.

4. **STATIC reference columns vs published findings.md** — programmatically diffed
   every cell of `STEP_REF` / `REF_27B` / `REF_CODER` (and the totals 7/8/8 and
   ~7/12, ~7/12) against
   `hardware-tests/qwen3.5-397b-vs-step3.7-flash-2026-05-29/findings.md`:
   **0 mismatches.** Includes the easy-to-get-wrong cells (p2_hallucination Coder
   1/3, p3_doc 27B 0/3, p3_market Coder 0/3, p3_business 27B 2/3). No fix to the
   reference columns was needed.

5. **Autopilot `--publish` scorecard math vs bench_report** — replicated
   `build_scorecard` via a read-only import of `arm_progress`. **Pass counts agree**
   (nothink 77, think 22; baseline delta 77−82 = −5, as intended).

## The one real fragility (documented + guarded, no behavior change)

The two publish tools use **different denominators** for "done":

- `bench_report.py`: a cell counts in the denominator iff **grade.json** exists.
- `bench_autopilot.py` `--publish` (`cell_done`): iff **summary.json +
  workspace_final.tar.gz** exist — i.e. *finished*, graded or not. An ungraded-but-
  finished cell is therefore counted in the autopilot denominator as a **non-pass**.

Live snapshot showed the gap concretely: p1_bugfix nothink = **5/5** (bench_report,
graded-only) vs **5/9** (autopilot, finished). Arm totals: 77/115 vs 77/119
(nothink), 22/36 vs 22/47 (think). At a clean COMPLETE run the gap closes (the
autopilot grades each arm after its run exits, so every finished cell gets a grade),
which is why the published artifacts normally agree. **But** the autopilot only needs
summary+tar to call a run COMPLETE — if end-of-run grading lags or partially fails,
`--publish` would emit a scorecard whose denominators silently disagree with
bench_report and whose pass-rate is understated, with no warning. That is the exact
unattended-failure case worth catching.

### Fix applied (bench_report.py, safe/standalone — the only file edited)
Added `cell_finished()` + `done_but_ungraded()` and a **reconciliation footnote** in
the scorecard section: if any cell has summary.json but no grade.json, the report now
prints a `⚠️ N finished-but-ungraded cell(s)` warning listing them, explaining that
these are excluded here but counted as non-pass by the autopilot scorecard, so the
two will disagree on x/N until grading completes — "expected empty on a clean
COMPLETE run; regrade before trusting the totals if present in a published doc."
Verified it fires correctly (8 cells at audit time, tracking the live run) and that
`--n 3/10/20` still generate cleanly with unchanged totals. Behavior is purely
additive; no existing output changed. bench_autopilot.py was NOT edited (live run).

## Lower-severity notes (NOT changed — would touch the live autopilot file)
- Autopilot scorecard's "Δ vs N=10 (nothink)" compares a per-task pass **count** at
  the run's N (e.g. 20) against the N=10 baseline count — a raw-count delta, not a
  rate delta. Defensible and labeled, but mildly misleading at N≠10. Left as-is.
- `cell_done` requiring workspace_final.tar.gz means a cell that grades but loses its
  tarball would be undercounted by the autopilot; none observed. Left as-is.

## Bottom line
Numbers check out. Scorecard, finish-reason audit, and redistribution are
self-consistent and match hand recounts; static reference columns exactly match the
published findings.md (0 mismatches, no ref fix needed). One genuine cross-tool
denominator divergence (only visible mid-run / on lagged grading) is now surfaced by
a non-destructive guard in bench_report.py.
