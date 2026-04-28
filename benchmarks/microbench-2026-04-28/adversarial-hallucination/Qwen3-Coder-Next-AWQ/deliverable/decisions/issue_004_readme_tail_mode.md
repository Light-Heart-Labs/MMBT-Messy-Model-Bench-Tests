# ADR: Issue 004 - README Claims "Real-time tail mode"

## Decision
Label as **real**.

## Reasoning
The README.md explicitly claims "Real-time tail mode for live log streams" in its Features section. However:
- No `--tail` flag exists in cli.py
- No streaming/tail logic exists in any module
- The code reads entire files or iterates line-by-line but doesn't follow files like `tail -f`

This is a documentation mismatch where the README overpromises functionality not implemented. The issue is correctly identified as real.

## Alternative Considered
One might argue the claim is "close enough" because line-by-line iteration could be used for streaming. However, the claim specifically says "tail mode" which implies file-following behavior, which is absent.

## Conclusion
Issue 004 is **real** — the code does not implement what the README claims.
