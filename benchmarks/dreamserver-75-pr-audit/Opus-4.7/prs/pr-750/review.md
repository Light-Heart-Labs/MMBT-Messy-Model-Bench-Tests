# PR #750 — Review notes

Reviewed against `prs/pr-750/raw/diff.patch` (3,790 lines of diff at audit
baseline `d5154c3`). Severity:

- ★★★ — must address before merge
- ★★ — would address before merge
- ★ — observation, not blocking

## Findings

### ★★★ — Existing maintainer CHANGES_REQUESTED unresolved

**Where:** `raw/files.json` `reviews` array shows three reviews from
`Lightheartdevs`: one COMMENTED + two CHANGES_REQUESTED (most recent
2026-04-22). The bodies describe substantive feedback. The PR has not
been updated since (`updatedAt: 2026-04-22T08:59:15Z`).

The auditor cannot speak to whether the reviews' specific asks are still
relevant — that's the maintainer's read. But: a CHANGES_REQUESTED PR with
no follow-up commits in five days isn't merge-ready, regardless of the
auditor's other findings.

**What to do:** Y should address (or push back on) the maintainer's
review comments and request re-review. After that, this audit's other
findings (★★ / ★ below) become the secondary checklist.

### ★★ — `amd-topo.sh` "fallback chain" smell

**Where:** `dream-server/installers/lib/amd-topo.sh` (the 460 added lines).

The PR body describes "three detection backends: amd-smi JSON, rocm-smi
text, sysfs NUMA/IOMMU fallback." `CLAUDE.md` is explicit: "No fallback
chains."

The auditor did **not** read every line of `amd-topo.sh`, so this is a
smell to verify, not a confirmed violation. Two ways the implementation
can be valid:

1. **Backend *selection*** — at startup, detect once which backend is
   available, then only ever use that one. Selection ≠ fallback.
2. **Backend *fallback*** — try amd-smi, fail, try rocm-smi, fail, try
   sysfs. This is the violation.

Y should say which it is in a comment in the file or a follow-up.

### ★★ — Compose-file rename is a breaking change for pinned users

**Where:** four `compose.multigpu.yaml` → `compose.multigpu-nvidia.yaml`
renames.

The `resolve-compose-stack.sh` change at line 2105 of the diff says
"Protects against renames across upgrades … where the cache would
otherwise hand docker stale paths." This is good — it explicitly addresses
the rename. But:

- The handler should be exercised by a test (the existing BATS
  `docker-phase.bats` doesn't cover compose-resolver renames).
- Users who pinned `docker-compose.multigpu.yml` in scripts outside
  DreamServer (e.g., a custom systemd unit) get a runtime error post-
  upgrade. This is the kind of thing a release note should call out.

### ★ — `2>/dev/null || true` patterns in phase 10 are pre-existing

**Where:** `installers/phases/10-amd-tuning.sh:2208,2214,2233,2234`.

These violate `CLAUDE.md` style. **However**, they're pre-existing
patterns in phase 10 (which is documented as the privileged OS-state
phase), not new in this PR. Worth a one-line note from Y that he's
inheriting the existing patterns rather than introducing them.

### ★ — `dream-cli` is in 15 open PRs' merge path; #750 makes it 16

**Where:** `dream-server/dream-cli` line 12 of `cluster_summary.json`
overlaps. Adding 289 lines + 45 deletions in #750.

The Yasin `dream-cli` cluster (14 PRs) all rebase against this. If #750
merges *before* the cluster, Yasin rebases once. If after, every Yasin
CLI PR rebases against #750. Recommendation in `analysis/dependency-graph.md`
puts #750 first.

### Convention adherence

- [x] No new `eval` of script output (verified: no `eval` patterns in diff)
- [x] No new `2>/dev/null` / `|| true` *introduced* — pre-existing patterns inherited from phase 10 (★ above)
- [?] No new fallback chains — **must verify in `amd-topo.sh`** (★★ above)
- [x] No port-binding changes
- [x] New file in `installers/lib/` (`amd-topo.sh`) is **pure** — verified by grep for `curl|wget|docker|systemctl|modprobe|sudo|redirected-writes|tee|>>` against the diff section: zero matches
- [x] New env vars added to **both** `.env.schema.json` (37 added) and `.env.example` (10 added)
- [x] No manifest changes that could break the resolver — manifest schema unchanged

## Tests run

The auditor cannot run AMD multi-GPU tests (no AMD multi-GPU hardware).
The author claims testing on 4× MI300X. The PR's BATS / pytest can be run
on a Linux VM without AMD hardware (mocking via fixtures), but that
exercises the *code*, not the *integration with real ROCm*. Integration
verification is the maintainer's responsibility; see
`tests/README.md`.

## Conclusion

Verdict: **REVISE — architectural rework remaining (per existing review).**
After Y addresses maintainer feedback, the auditor recommends a real-
hardware verification pass before MERGE.

**Cherry-pick recommendation:** Yank the 1-line BATS fix to a separate
trivial PR and merge it on `main` first to unblock 72 PR CI signals.
