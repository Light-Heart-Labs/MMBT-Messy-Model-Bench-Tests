# PR #1011 — Verdict

> **Title:** chore(bash32): guard declare -A callers + route dream-cli validate through $BASH
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** True · **Base:** `main`  ←  **Head:** `chore/bash32-declare-a-audit`
> **Diff:** +43 / -3 across 6 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1011

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 2 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **4** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE — promote from draft.** Adds Bash 4+ guards to five scripts that use
`declare -A` (`scripts/pre-download.sh`, `scripts/dream-test-functional.sh`,
`scripts/validate-env.sh`, `lib/progress.sh`,
`installers/phases/03-features.sh`) and prefixes
`scripts/validate-env.sh` and `scripts/validate-manifests.sh` invocations in
`dream-cli:1117,1125` with `"$BASH"` so they inherit dream-cli's modern bash.
This is the right model: dream-cli already guards Bash 4+ at line 9, so
`$BASH` is guaranteed to point at a modern interpreter. Without this, macOS
users running with stock `/bin/bash` 3.2 hit cryptic
`declare -A: invalid option` crashes when invoking these scripts directly,
and `dream config validate` was silently non-functional because the
shebang-launched subprocesses re-resolved to system bash.

## Findings

- Pattern A (standalone scripts) and Pattern B (sourced libs) are both
  cleanly differentiated. Pattern B's
  `return 1 2>/dev/null || exit 1` mirrors `lib/service-registry.sh:18-24`
  exactly; sourced-vs-direct invocation both behave correctly.
- Drops a dead `2>/dev/null || true` fallback at
  `dream-test-functional.sh:34` (`declare -A SERVICE_PORTS`) — that fallback
  was never going to help on Bash 3.2 (the syntax error happens at parse
  time, before the trap can catch). Replacing it with the explicit guard
  is correct.
- The `"$BASH"` prefix is the right idiom. Less brittle than relying on PATH
  to surface a modern bash; works regardless of how the user installed bash.
- Currently draft per the PR header. The body says shellcheck is clean and
  manual macOS testing under Bash 3.2.57 verified the friendly error messages
  fire. Promote and land — no obvious blocker.

## Cross-PR interaction

- `dream-cli` conflict surface with the rest of the dream-cli stack is
  unavoidable. Per dependency-graph, this should land alongside #1006/#1007/#1008
  rather than after the full stack. Two-line touch on dream-cli, low conflict
  risk.
- `installers/phases/03-features.sh` is touched by #1043 (already verdicted
  MERGE). Different region; trivial textual merge.

## Trace

- `dream-server/dream-cli:1117,1125` — `"$BASH"` prefix
- `dream-server/scripts/pre-download.sh:20-26` — Pattern A guard
- `dream-server/scripts/validate-env.sh:10-16` — Pattern A guard
- `dream-server/scripts/dream-test-functional.sh:14-20,34` — Pattern A guard +
  drop dead fallback
- `dream-server/lib/progress.sh:5-11` — Pattern B guard
- `dream-server/installers/phases/03-features.sh:23-29` — Pattern B guard
