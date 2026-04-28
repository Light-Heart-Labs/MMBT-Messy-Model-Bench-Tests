# ADR-001: Issue 009 — `format_legacy()` wrong file citation

## Context

Issue 009 claims that `format_legacy()` in `output.py` is unused dead code.

## Investigation

- `format_legacy()` does exist in the codebase, but in `logalyzer/utils.py:21`, not `output.py`.
- `output.py` contains: `to_json()`, `to_csv()`, `to_text()`, and `render_aggregate()`. No `format_legacy()`.
- `format_legacy()` in `utils.py` is also unused (no other module imports it).

## Decision

**Verdict: fabricated**

Per the rules: "A wrong file citation makes the issue fabricated. If issue 009 claims a function is in `output.py` but the function actually lives in `utils.py`, the issue as written is fabricated."

The underlying observation (that `format_legacy()` is dead code) is correct, but the claim as written — that it lives in `output.py` — is false. The reviewer either misread the code or hallucinated the location.

## Notes

If a human reviewer were triaging this, they might file a corrected issue: "format_legacy() in utils.py is unused dead code." But as a verification of the original claim, it fails.
