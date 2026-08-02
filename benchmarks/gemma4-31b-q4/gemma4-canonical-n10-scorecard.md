# Gemma 4 31B Q4 raw canonical scorecard (N=10)

> Raw grader verdicts only. Any reproducible correction is a separate overlay tied to unchanged archive and grader hashes.

- Evidence-complete runs: 120/120
- Normal completed workspaces: 120/120
- Explicit terminal outcomes: 0/120
- Graded runs: 120/120
- Raw pass-equivalent outcomes: 89/120
- Median model-call completion throughput: 55.85 tok/s
- Median cell wall time: 113.05 s
- Telemetry-complete runs: 118/120

| Task | Raw pass | Scored | Finish reasons | Quality outcomes |
|---|---:|---:|---|---|
| `p1_bugfix` | 4/10 | 10/10 | done_signal:10 | FAIL:6, PASS:4 |
| `p1_testwrite` | 8/10 | 10/10 | done_signal:10 | FAIL:2, PASS:8 |
| `p1_refactor` | 7/10 | 10/10 | done_signal:10 | FAIL:3, PASS:7 |
| `p2_extract` | 10/10 | 10/10 | done_signal:10 | PASS:10 |
| `p2_ci` | 10/10 | 10/10 | done_signal:10 | PASS:10 |
| `p2_hallucination` | 6/10 | 10/10 | done_signal:6, model_stopped:4 | MISSING_OUTPUT:4, PASS:6 |
| `p2_triage` | 8/10 | 10/10 | done_signal:10 | FAIL:2, PASS:8 |
| `p3_doc` | 10/10 | 10/10 | done_signal:10 | PASS:10 |
| `p3_business` | 6/10 | 10/10 | done_signal:10 | FAIL:4, PASS:6 |
| `p3_market` | 10/10 | 10/10 | done_signal:10 | STRUCTURAL_PASS:10 |
| `p3_writing` | 10/10 | 10/10 | done_signal:10 | PASS:10 |
| `p3_pm` | 0/10 | 10/10 | done_signal:10 | FAIL:10 |

## Methodology boundary

A `done_signal` is a finish behavior, not a pass. `PASS` and `STRUCTURAL_PASS` count only as raw pass-equivalent grader verdicts. A preserved terminal label is reported as a distinct non-pass quality outcome, never fabricated into a normal grader verdict. Model-call throughput excludes tool execution; wall time includes it. Telemetry is per attributed replica GPU, while CPU package power is shared host context and AC wall power is unavailable to software.
