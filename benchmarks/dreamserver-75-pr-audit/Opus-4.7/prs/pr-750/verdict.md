# PR #750 — Verdict

> **Title:** feat: AMD Multi-GPU Support
> **Author:** [y-coffee-dev](https://github.com/y-coffee-dev) ("Y" / Youness, AMD multi-GPU specialist) · **Draft:** False · **Base:** `main`  ←  **Head:** `feat/amd-multi-gpu`
> **Diff:** +3,092 / -145 across 33 file(s) · **Risk tier: Medium (score 12/20)**
> **PR URL:** https://github.com/Light-Heart-Labs/DreamServer/pull/750

## Risk score

| Axis | Score | Why |
|------|------:|-----|
| A — Surface area | 4 | 33 files; new lib (`amd-topo.sh`), 3 new compose overlays, 4 file renames, dashboard-api Python, CLI, schema, tests |
| B — Test coverage | 2 | Strong: 484-line BATS, 313-line shell test, 431-line pytest, fixture files. Author tested on real 4×MI300X. **But** auditor cannot exercise on real hardware. |
| C — Reversibility | 1 | Schema additions are backwards-compatible (new keys with defaults). Compose renames are a breaking change for users who pinned the old `multigpu.yml` filename, but the resolver auto-discovers them. |
| D — Blast radius | 4 | Touches AMD installer paths, phase 10 (sysctl/modprobe/GRUB territory), and the resolver. AMD partnership means an AMD regression has external relationship costs. |
| E — Contributor | 1 | Y has prior AMD-specific contributions; the PR shows deep familiarity. Score 1 (not 0) only because cross-architecture changes (NVIDIA overlay rename) are outside Y's usual surface. |
| **Total** | **12** | **Medium** |

## Verdict

**REVISE — architectural rework remaining (per existing review feedback), then MERGE pending real-hardware verification.**

The architecture is sound. Topology library at `installers/lib/amd-topo.sh`
is **pure** (verified — no shell side-effects in the diff: no `curl`,
`wget`, `docker`, `systemctl`, `modprobe`, `sudo`, redirected writes, or
network access). It honors the lib/phases purity boundary that
`research/upstream-context.md` §3 documents. CI is green on every check
including matrix-smoke for all 6 distros and the new `validate-compose`
workflow this PR adds.

The test coverage is unusual *for the better*: 25 BATS unit + 23 integration
+ 16 pytest, with real-hardware fixture files extracted from 4×AMD Instinct
MI300X. The maintainer should not need to ask Y for more tests; he should
ask whether the test budget cleared the **CHANGES_REQUESTED** items the
maintainer's earlier review identified.

**Cannot finish-merge from this audit's environment.** Real-hardware
verification on multi-GPU AMD is out of scope (no MI300X / no Strix Halo
on the auditor's box). The verdict's last step belongs to the maintainer
with hardware access — likely Y himself, on the rig he tested on.

## Side benefit — fixes the BATS regression poisoning 72 PRs

`tests/bats-tests/docker-phase.bats:100` is also patched in this PR
(line 2963 of `raw/diff.patch`):

```diff
-    assert_output $'sudo\ndocker'
+    assert_output "sudo docker"
```

This is the **same fix** I documented in
`testing/reproductions/repro-bats-docker-cmd-arr.sh` (see
`research/questions.md` Q1). Merging #750 alone would turn the
`integration-smoke` job green for itself; merging the BATS-only piece
out-of-band onto `main` would do the same for the other 71 PRs.

**Strategic recommendation:** Cherry-pick that 1-line bats fix from #750
to a separate trivial PR and merge it on `main` *first*. Reasons:
- 72 PR CI signals become reliable immediately
- Reviewers can trust the matrix-smoke/distro green for the next batch
  of PRs without diff inspection of integration-smoke logs
- It doesn't pre-empt #750; #750's other 32 files still ship as a unit

The cherry-pick takes ~5 minutes; the maintainer can close the
cherry-picked PR as "merged via X" once #750 lands.

## Specific items to confirm with Y before merge (independent of the
maintainer's existing CHANGES_REQUESTED feedback)

- [ ] **Compose-rename upgrade path.** PR header notes "Protects against
      renames across upgrades (e.g. multigpu.yml → multigpu-nvidia.yml)
      where the cache would otherwise hand docker stale paths." Verify this
      handler is exercised by an upgrade-from-2.4-with-multigpu test, not
      just the green-field install path.
- [ ] **`amd-topo.sh:detect_amd_topo` failure mode.** The PR body describes
      "three detection backends: amd-smi JSON, rocm-smi text, sysfs
      NUMA/IOMMU fallback". The fallback chain is *exactly* the kind of
      pattern `CLAUDE.md` discourages ("No fallback chains"). Verify that
      each backend's selection is exclusive (e.g., the topology source is
      detected once and used; we don't try-fail-try) — i.e. it's
      *backend selection*, not *retry-with-different-tool*.
- [ ] **Phase 10 GRUB toggling.** The diff still uses `sudo -n sed`,
      `sudo -n update-grub`, and `2>/dev/null || true` patterns. These are
      *pre-existing* in phase 10 (the brief documents phase 10 as the
      privileged OS-state phase) and the PR doesn't make it worse — but
      worth confirming Y is aware of `CLAUDE.md`'s style rules and
      consciously inheriting the existing patterns.

## Cross-PR interaction

| Other PR | Relationship |
|----------|--------------|
| #1043 (Y) | Y's other open PR. Same author; no overlap. Independent. |
| Yasin's `dream-cli` cluster (15 PRs) | #750 modifies `dream-cli` (289 lines). When merged, all 15 of Yasin's CLI PRs need re-rebase against #750's CLI changes. **Recommendation:** merge #750 *before* the Yasin CLI cleanup sweep so Yasin rebases once. |
| #988 (loopback) | #750 doesn't change bind addresses; no semantic conflict. |
| #1027 (BIND_ADDRESS for community extensions) | No overlap. |

## Trace

- AMD topology library: `dream-server/installers/lib/amd-topo.sh` (new, 460 lines)
- Compose rename: `docker-compose.multigpu.yml` → `docker-compose.multigpu-nvidia.yml` (and 3 sister renames in `extensions/services/`)
- Existing review thread: `Lightheartdevs` left CHANGES_REQUESTED twice (visible in `raw/files.json`)
- BATS fix included: `tests/bats-tests/docker-phase.bats:100` — see `research/questions.md` Q1
- `validate-compose.yml` workflow: new in this PR
