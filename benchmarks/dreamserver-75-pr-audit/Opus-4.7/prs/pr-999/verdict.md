# PR #999 — Verdict

> **Title:** feat(dream-cli): Apple Silicon coverage for gpu subcommands and doctor
> **Author:** [yasinBursali](https://github.com/yasinBursali) · **Draft:** False · **Base:** `main`  ←  **Head:** `fix/dream-cli-apple-silicon-coverage`
> **Diff:** +79 / -5 across 2 file(s) · **Risk tier: Low (score 4/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/999

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 1 | _see review.md_ |
| B — Test coverage | 2 | _see review.md_ |
| C — Reversibility | 0 | _see review.md_ |
| D — Blast radius | 1 | _see review.md_ |
| E — Contributor | 0 | _see review.md_ |
| **Total** | **4** | **Low** |

Methodology: [`decisions/0001-risk-scoring-methodology.md`](../../decisions/0001-risk-scoring-methodology.md).

## Verdict

**MERGE.** Adds correct Apple Silicon branches to `cmd_status_json`, `_gpu_status`, `_gpu_topology`, `_gpu_validate`, `_gpu_reassign` in `dream-cli`, and fixes two genuine bugs in `scripts/dream-doctor.sh`: RAM via `sysctl hw.memsize` on Darwin (was reading non-existent `/proc/meminfo`, returning 0 GB), and disk via POSIX `df -k` (was `df -BG`, GNU-only — broken on macOS and BSD). All Apple-specific code is gated on `${GPU_BACKEND:-}" == "apple"`, so Linux NVIDIA/AMD and Windows behavior is unchanged. The doctor's `gpu_backend` compatibility check is skipped on Apple to suppress the ~18 false-positive autofix hints per run that the body cites.

## Findings

- **Backend-selection branching, not retry/fallback.** Each new Apple-Silicon block is gated on `GPU_BACKEND=apple` — that's CLAUDE.md-compliant platform branching, not a fallback chain. `_gpu_status` previously had `nvidia` and `amd` branches and a generic warning fallthrough; this PR inserts `apple` as a peer branch with intent-appropriate output (chip name, unified memory, GPU cores via `system_profiler`).
- **`/v1/models`-style `system_profiler` parse uses `2>/dev/null || echo "?"`.** Defensive on `system_profiler` exit code, but the failure mode is bounded — worst case the GPU core count shows `?`. Same pattern as the schema fallback in PR #994. CLAUDE.md tolerates these scoped probes.
- **`HOST_RAM_GB` `.env` fallback is a nice belt-and-suspenders.** `dream-doctor.sh:65-69` adds: if RAM detection returns 0 *and* `.env` has `HOST_RAM_GB=...`, trust the installer-recorded value. Useful in containerized/CI scenarios where `sysctl` is unavailable.
- **Convention adherence:** No `eval`, no port bindings, no `installers/lib/` changes. Schema/example: no env additions.

## Cross-PR interaction

- Cluster 1 conflict file. Per `analysis/dependency-graph.md`, the recommended merge order has #999 after #1000. Textual conflicts only — independent code blocks.
- Listed in `analysis/dependency-graph.md` as "consolidation candidate" with PR #1016 (also Apple-silicon CLI polish, also Yasin, currently DRAFT). Maintainer could ask Yasin to consolidate, but this PR stands on its own.
- No overlap with PR #1043 (Y/Youness Custom-mode fix) despite both touching installer-adjacent paths — different files.

## Trace

- `dream-server/dream-cli:704-722` — `cmd_status_json` Apple branch returning `{backend, chip, unified_memory_gb, gpu_cores}`.
- `dream-server/dream-cli:2592-2606` — `_gpu_status` Apple branch.
- `dream-server/dream-cli:2632-2635, 2774-2782, 2872-2875` — Apple guards on topology / validate / reassign.
- `dream-server/scripts/dream-doctor.sh:60-69` — `sysctl hw.memsize` for Darwin RAM + `HOST_RAM_GB` fallback.
- `dream-server/scripts/dream-doctor.sh:74` — POSIX `df -k` (was GNU `df -BG`).
- `dream-server/scripts/dream-doctor.sh:200` — Apple-skips the `gpu_backend` compatibility check.
