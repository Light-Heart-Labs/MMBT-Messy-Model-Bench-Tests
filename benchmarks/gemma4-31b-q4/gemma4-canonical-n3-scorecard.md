# Gemma 4 31B Q4 raw canonical scorecard (N=3)

> Raw grader verdicts only. Any reproducible correction is a separate overlay tied to unchanged archive and grader hashes.

- Evidence-complete runs: 36/36
- Normal completed workspaces: 36/36
- Explicit terminal outcomes: 0/36
- Graded runs: 36/36
- Raw pass-equivalent outcomes: 29/36
- Median model-call completion throughput: 54.5 tok/s
- Median cell wall time: 122.8 s
- Telemetry-complete runs: 34/36

| Task | Raw pass | Scored | Finish reasons | Quality outcomes |
|---|---:|---:|---|---|
| `p1_bugfix` | 2/3 | 3/3 | done_signal:3 | FAIL:1, PASS:2 |
| `p1_testwrite` | 2/3 | 3/3 | done_signal:3 | FAIL:1, PASS:2 |
| `p1_refactor` | 3/3 | 3/3 | done_signal:3 | PASS:3 |
| `p2_extract` | 3/3 | 3/3 | done_signal:3 | PASS:3 |
| `p2_ci` | 3/3 | 3/3 | done_signal:3 | PASS:3 |
| `p2_hallucination` | 2/3 | 3/3 | done_signal:2, model_stopped:1 | MISSING_OUTPUT:1, PASS:2 |
| `p2_triage` | 3/3 | 3/3 | done_signal:3 | PASS:3 |
| `p3_doc` | 3/3 | 3/3 | done_signal:3 | PASS:3 |
| `p3_business` | 2/3 | 3/3 | done_signal:3 | FAIL:1, PASS:2 |
| `p3_market` | 3/3 | 3/3 | done_signal:3 | STRUCTURAL_PASS:3 |
| `p3_writing` | 3/3 | 3/3 | done_signal:3 | PASS:3 |
| `p3_pm` | 0/3 | 3/3 | done_signal:3 | FAIL:3 |

## Methodology boundary

A `done_signal` is a finish behavior, not a pass. `PASS` and `STRUCTURAL_PASS` count only as raw pass-equivalent grader verdicts. A preserved terminal label is reported as a distinct non-pass quality outcome, never fabricated into a normal grader verdict. Model-call throughput excludes tool execution; wall time includes it. Telemetry is per attributed replica GPU, while CPU package power is shared host context and AC wall power is unavailable to software.
