# PR #1023 — Verdict

> **Title:** fix(scripts): SIGPIPE-safe first-line selection in 5 scripts
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/shell-sigpipe-sweep-4scripts`
> **Diff:** +6 / -6 across 5 file(s) · **Risk tier: Trivial (score 1/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/1023

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 0 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 0 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **1** | **Trivial** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Six mechanical `head -1`/`head -n 1` → `sed -n '1p'` substitutions across five scripts running under `set -euo pipefail`. The trigger is real: multi-GPU `nvidia-smi` (multiple lines) + `head -1` closing stdin produces SIGPIPE/exit-141 in the upstream stage, which `pipefail` then re-raises. `sed -n '1p'` consumes the full stream before exiting, breaking the SIGPIPE chain. Same fidelity on BSD and GNU sed.

## Findings

- The pre-existing `2>/dev/null` and `|| true` patterns are retained — they predate this PR and are not regressions per the audit's "exception: pre-existing patterns in main aren't regressions" rule. PR doesn't add any new ones.
- Multi-GPU NVIDIA hosts (the partnership target per `upstream-context.md` §11) are the primary beneficiaries; without this fix `pre-download.sh:112` and `dream-preflight.sh:87` SIGPIPE on any 2-GPU box.
- No tests added. For a six-line mechanical fix in shell scripts where the failure mode is "exit 141 instead of expected output", manual reproduction on multi-GPU is the appropriate verification.

## Cross-PR interaction

- No file overlap with other open PRs in this batch. None of the dream-cli cluster PRs (#993-#1020) touch these specific files.
- Independent of the host-agent and dashboard-api clusters.

## Trace

- `installers/macos/dream-macos.sh:158` — `read_env_value` first match
- `installers/macos/lib/env-generator.sh:39, 51` — `read_env_value`, `read_searxng_secret`
- `scripts/check-offline-models.sh:27` — first GGUF
- `scripts/dream-preflight.sh:87` — first-GPU memory.free
- `scripts/pre-download.sh:112` — first-GPU memory.total
