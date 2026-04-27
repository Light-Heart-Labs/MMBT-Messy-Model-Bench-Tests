# PR #1020 — Summary

> What the PR claims to do, paraphrased by the auditor. The actual
> diff-vs-claim comparison is in `diff-analysis.md`.

## Title (verbatim)

> test: contract + mock coverage for Apple Silicon GPU backends

## Author's stated motivation

The PR body says (paraphrased):

> ## ⚠️ Draft — depends on #999 merging first

#999 (`fix/dream-cli-apple-silicon-coverage`) introduces the 5 Apple `GPU_BACKEND=apple` code paths (`_gpu_status`, `_gpu_topology`, `_gpu_validate`, `_gpu_reassign`, `cmd_status_json`) plus a Darwin branch in `scripts/dream-doctor.sh` (RAM via `sysctl hw.memsize`, POSIX `df -k`). This PR adds regression shields for all of them.

Once #999 merges, rebase drops the merge commit and the PR diff becomes 2 new test files (138 + 321 LoC).

## What
Two new test files locking in Apple-Silicon behavior:

### `tests/contracts/test-dream-doctor.sh` (138 lines, 5 cases, Darwin-guarded)
- `dream-doctor.sh` exits 0 under `GPU_BACKEND=apple`
- `.preflight.inputs.ram_gb` > 0 (sysctl hw.memsize path)
- `.preflight.inputs.disk_gb` > 0 (POSIX df -k on $HOME)
- `.autofix_hints` has 0 "incompatible with current GPU backend" entries under apple backend
- Empty-sysctl stub forces fallback to `.env` `HOST_RAM_GB` (writes/removes .env; pre-existing .env → SKIP)

Skips cleanly on Linux CI via `[[ "$(uname -s)" == "Darwin" ]] || skip`.

### `tests/test-gpu-apple.sh` (321 lines, 21 cases)
Hermetic PATH-stub pattern (sysctl, system_profiler, curl, docker all PATH-prepended). `nvidia-smi` intentionally absent so `command -v nvidia-smi` returns false under the apple branch tests.

- `gpu status` (apple): rc=0 + header + Chip/Unified-memory/GPU-cores output + stub chip reflected
- `gpu topology` (apple): "Single integrated GPU" + rc=0
- `gpu validate` (apple): "  …(truncated)

## Auditor's one-line restatement

_TBD — auditor restates the PR in their own words after reading the diff._

## Bounty tier (claimed / inferred)

_Not labeled in metadata. Inferred from scope — see `report/contributor-notes.md`._
