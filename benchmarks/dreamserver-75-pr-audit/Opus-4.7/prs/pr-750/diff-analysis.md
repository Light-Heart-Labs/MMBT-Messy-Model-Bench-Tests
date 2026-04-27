# PR #750 — Diff analysis

What the diff actually changes vs what the title/body claim.

## Files touched (33)

By area:

| Area | Files | + | - |
|------|-------|--:|--:|
| **AMD topology lib** | `installers/lib/amd-topo.sh` (new) | 460 | 0 |
| **Detection** | `installers/lib/detection.sh`, `installers/phases/02-detection.sh` | 98 | 26 |
| **Installer phases** | `installers/phases/{03-features,06-directories,10-amd-tuning}.sh` | 68 | 24 |
| **Compose overlays (new)** | `docker-compose.multigpu-amd.yml` + 3 service overlays | 81 | 0 |
| **Compose overlays (renamed)** | `docker-compose.multigpu.yml` → `multigpu-nvidia.yml` (+ 3 service overlays) | 0 | 0 (pure rename) |
| **CLI** | `dream-cli` | 289 | 45 |
| **Scripts** | `assign_gpus.py`, `classify-hardware.sh`, `resolve-compose-stack.sh` | 68 | 20 |
| **Dashboard API** | `extensions/services/dashboard-api/gpu.py` | 47 | 18 |
| **GPU database** | `config/gpu-database.json` | 160 | 0 |
| **CI** | `.github/workflows/validate-compose.yml` (new), test files | 79 | 0 |
| **Schema/example** | `.env.schema.json`, `.env.example` | 47 | 11 |
| **Tests** | BATS, shell, pytest, real-hardware fixture files | ~1,650 | 0 |
| **BATS regression fix** | `tests/bats-tests/docker-phase.bats:100` | 1 | 1 |

## Auditor's read

The diff matches the title precisely. Five categories of change:

1. **AMD topology detection** — `installers/lib/amd-topo.sh` (new, 460
   lines). Pure-functional bash library; no shell side effects (verified
   by grep for `curl|wget|docker|systemctl|modprobe|sudo|tee|>>` against
   the file's diff section, zero matches).

2. **Installer phase integration** — `02-detection.sh` calls into
   `amd-topo.sh::detect_amd_topo` when `GPU_COUNT > 1` and backend is AMD.
   `06-directories.sh` writes the AMD multi-GPU env vars to `.env`.
   `10-amd-tuning.sh` adds render-node verification.

3. **Compose layering** — three new AMD-multi-GPU compose overlays for
   llama-server, comfyui, embeddings, whisper. Four rename hops where
   the generic `multigpu.{yml,yaml}` becomes `multigpu-nvidia.{yml,yaml}`
   for symmetry. The resolver picks up the new names automatically;
   `resolve-compose-stack.sh:2105` adds a cache-flush handler for the
   upgrade case.

4. **Surface-area extensions** — `dream-cli` learns AMD-specific paths
   for `gpu status / topology / assign / reassign / monitor`. Dashboard
   API gains AMD GPU monitoring via `amd-smi` and sysfs hwmon.
   `gpu-database.json` gains AMD device entries.

5. **Test coverage** — 484-line BATS `amd-topo.bats`, 313-line shell
   `test-amd-topo.sh`, 431-line pytest `test_gpu_amd.py`, and five real-
   hardware fixture files extracted from 4×MI300X. Plus 79 lines of new
   `validate-compose.yml` workflow and 86 lines of installer contract
   tests.

## Surprises

- **One file is the BATS test fix that's poisoning 72 of 75 PR CI runs.**
  Line 2963 of `raw/diff.patch`: `tests/bats-tests/docker-phase.bats:100`
  changes `assert_output $'sudo\ndocker'` to `assert_output "sudo docker"`.
  This is **not** described in the PR body. Cherry-picking that one line
  to its own trivial PR is the highest-leverage move in the queue (see
  `verdict.md`).

- **`integration-smoke: SUCCESS` on this PR's CI** — because of the BATS
  fix above. Every other open PR shows FAILURE on integration-smoke.
  This single PR has the fix bundled into a 33-file feature.

## What the diff doesn't include (confirmation, not gap)

- **No port-binding changes.** This is a feature-add, not a security PR.
  Compose overlays use the existing `${BIND_ADDRESS}` knob via the base
  files they layer on top of.
- **No host-agent changes.** The host-agent has no AMD-specific surface;
  this PR doesn't touch `bin/dream-host-agent.py`.
- **No openclaw / ape changes.** Agent framework is GPU-agnostic.
