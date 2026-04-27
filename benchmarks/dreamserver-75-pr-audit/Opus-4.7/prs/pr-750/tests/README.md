# Tests run for PR #750

The PR adds substantial test coverage:
- 484-line `tests/bats-tests/amd-topo.bats`
- 313-line `tests/test-amd-topo.sh` shell
- 431-line `extensions/services/dashboard-api/tests/test_gpu_amd.py`
- 86 added lines in `tests/contracts/test-installer-contracts.sh`
- Five real-hardware fixture files (`amd_smi_*`, `rocm_smi_*`)
- 79-line `.github/workflows/validate-compose.yml`

Author reports verifying on real 4× AMD Instinct MI300X hardware.

## What this audit ran

**Cannot test on real AMD hardware** (no MI300X / no Strix Halo on the
auditor's box). The CI signal at the time of audit shows every check
green for this PR (including matrix-smoke ×6 distros, validate-compose,
macos-smoke). That is third-party verification of everything except the
real-hardware path.

The author's `amd-topo.bats` and `test-amd-topo.sh` use mocked tool output
(fixture files), which exercises code paths *without* needing real
hardware. Those are runnable on the auditor's Windows box via Docker, but
the auditor did not run them — the *PR's CI* already ran them, and CI is
green. Re-running locally would be redundant.

## What the maintainer should run before merge

1. **Real-hardware integration test** on an AMD multi-GPU rig
   (the author's MI300X setup, or any 2+ AMD GPU machine).
2. **Upgrade-from-2.4 path** to confirm the compose-rename cache-flush
   handler actually runs (per `review.md` ★★ Compose-file rename).
3. **Re-review the existing CHANGES_REQUESTED items** that haven't been
   addressed since 2026-04-22.

## Tests not run (and why)

- Real AMD multi-GPU hardware: not available to auditor.
- Apple Silicon overlap with `gpu.py` (#1025): future merge-order check,
  not relevant to #750 standalone.
