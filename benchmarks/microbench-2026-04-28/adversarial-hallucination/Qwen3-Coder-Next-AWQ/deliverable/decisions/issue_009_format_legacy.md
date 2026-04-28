# ADR: Issue 009 - format_legacy() Dead Code

## Decision
Label as **real**.

## Reasoning
The `format_legacy()` function exists in utils.py:21 but:
- It is never imported by any module
- It is never called anywhere in the codebase
- The comment in the function itself says "No longer used internally"

This is a textbook case of dead code that should be removed unless external scripts depend on it (which would be documented).

## Alternative Considered
One might argue the function serves as a public API for external users. However, there's no documentation or test coverage for it, and the CLI doesn't expose it. Without evidence of usage, it's dead code.

## Conclusion
Issue 009 is **real** — `format_legacy()` is unused and should be removed or documented as a public API with tests.
