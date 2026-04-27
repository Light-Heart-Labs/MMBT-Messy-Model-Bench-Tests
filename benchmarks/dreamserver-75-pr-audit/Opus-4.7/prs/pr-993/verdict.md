# PR #993 — Verdict

> **Title:** fix(dream-cli): color-escape + table-separator + NO_COLOR spec
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dream-cli-visual-polish`
> **Diff:** +56 / -16 across 1 file(s) · **Risk tier: Trivial (score 2/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/993

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 1 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **2** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Three correct, well-scoped polish fixes in `dream-cli`. (1) `dream-cli:34-46` — color variables move from single-quoted `'\033[...'` (which stores the literal backslash-zero-three-three string, fine for `echo -e` but broken inside heredocs that don't re-interpret escapes) to ANSI-C-quoted `$'\033[...'` (which stores the actual ESC byte). Wrapped in `[[ -t 1 ]] && [[ -z "${NO_COLOR+x}" ]]` so colors get suppressed on non-TTY output. (2) New `hr <width>` helper at `:71-77` using `printf -v` + `${var// /<char>}` parameter expansion to render Unicode `─` separators at the actual column width. (3) `${NO_COLOR+x}` is the spec-correct check per [no-color.org](https://no-color.org/) — it treats `NO_COLOR=""` as "set" rather than "empty unset," matching the spec. The pre-existing literal-escape leak into `cmd_help`'s heredoc is fixed.

## Findings

- **The TTY guard is the load-bearing change.** `dream help > out.txt` previously emitted literal `\033[0;34m` text into the file; now it emits no escapes. This is the kind of paper-cut polish that improves CLI scriptability — `dream list | jq ...` still won't parse (use `--json`, see PR #1000) but no escape codes leak.
- **Dynamic-width separator in `_template_list:3122-3151` is a real correctness improvement.** Hard-coded `"----"` separators produced visible gaps under `%-20s` padding. The new `hr "$max_id_len"` etc. computes per-column widths in a first pass, emits the separator in a second pass.
- **Convention adherence:** No `eval`, no new `2>/dev/null` / `|| true`, no retry chains, no port bindings. Pure `dream-cli`-only change.

## Cross-PR interaction

- Touches `dream-cli` — the central conflict file in `analysis/dependency-graph.md` Cluster 1. The dependency graph proposes merge order `#1006 (log → stderr) → #1007 → #1008 → #993 → #994 → #997 → #1000 → #999 → #998 → #1002 → ...`. **This PR is "Yasin polish step 4" in that chain.** Textual conflicts with #994/#997/#998/#999/#1000/#1002 are mechanical (different code blocks); no semantic conflicts.
- The TTY guard at `:34-46` overlaps with PR #998's `set -eo pipefail` line at `:6` — independent lines.

## Trace

- `dream-server/dream-cli:34-46` — TTY+NO_COLOR-guarded color block using ANSI-C quoting.
- `dream-server/dream-cli:71-77` — new `hr <width> [<char>]` helper.
- `dream-server/dream-cli:1679, 1848` — table separators in `cmd_list` and `cmd_preset list` use `hr`.
- `dream-server/dream-cli:3122-3151` — dynamic-width separator logic in `_template_list`.
