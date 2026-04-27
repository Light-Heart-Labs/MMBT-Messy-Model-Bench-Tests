# Decision Records

## ADR-001: Risk Scoring Methodology

**Date:** 2026-04-27
**Status:** Accepted

**Context:** We need a consistent way to score PR risk across 75 PRs from 8 contributors.

**Decision:** Use 5 axes (Surface Area, Test Coverage, Reversibility, Blast Radius, Contributor Track), each scored 1-5. Composite score determines risk level.

**Rationale:**
- Surface Area: Counted by unique files. 100+ files = 5.
- Test Coverage: PRs with tests get -1. No tests = 4-5.
- Reversibility: Data migrations = 4-5. Simple code changes = 1-2.
- Blast Radius: Core files (host-agent, dream-cli) = 3-4. Edge files = 1-2.
- Contributor Track: yasinBursali (63 PRs) = 1. First-time = 4-5.

**Consequences:** yasinBursali PRs score Low-Medium. Large PRs from new contributors score High-Critical.

---

## ADR-002: Supersession Criteria

**Date:** 2026-04-27
**Status:** Accepted

**Context:** Multiple PRs touch the same files with overlapping functionality.

**Decision:** A PR is superseded when:
1. Another open PR includes all of its changes plus more
2. Another open PR achieves the same goal with a better approach
3. The PR is a dependency bump included in a larger PR

**Rationale:** Prevents duplicate merges and reduces maintainer burden.

**Consequences:**
- #1037 superseded by #1045
- #351 superseded by #364
- #716 superseded by #364
- #991 superseded by #983
- #990 superseded by #983

---

## ADR-003: Merge Order for Interdependent PRs

**Date:** 2026-04-27
**Status:** Accepted

**Context:** Many PRs from yasinBursali are interdependent (host-agent chain, CLI chain).

**Decision:** Merge in dependency order:
1. Security baseline first (#988)
2. Foundation PRs next (#1030, #998)
3. Feature PRs after (#1057, #1002, etc.)

**Rationale:** Each PR builds on the previous. Merging out of order would cause conflicts.

**Consequences:** The host-agent chain (7 PRs) and CLI chain (12 PRs) must be merged in specific order.

---

## ADR-004: Mobile Support Out of Scope

**Date:** 2026-04-27
**Status:** Accepted

**Context:** PR #961 adds Android Termux and iOS a-Shell support.

**Decision:** Reject for fit — mobile support is out of scope for the current roadmap.

**Rationale:** The project's GPU-dependent architecture requires desktop/server hardware. Mobile devices lack the GPU resources for meaningful inference. Supporting mobile would require a fundamentally different product.

**Consequences:** PR #961 is rejected. If mobile is a strategic goal, it should be a separate project.

---

## ADR-005: Extensions Library Pruning Recommendation

**Date:** 2026-04-27
**Status:** Recommendation (requires maintainer decision)

**Context:** Three PRs (#351, #364, #716) each add 150k+ lines to the extensions library.

**Decision:** Recommend pruning the extensions library to 10-15 core services. Archive the rest as community-contributed extensions.

**Rationale:** The current 33+ services create unmanageable PR sizes. Each new service adds compose files, manifests, READMEs, and GPU overlays. The maintenance burden grows linearly.

**Consequences:** Requires maintainer decision. If accepted, PRs #351, #364, and #716 would need to be re-scoped.

---

## ADR-006: AMD Multi-GPU Fast-Track

**Date:** 2026-04-27
**Status:** Recommendation (requires AMD partnership sign-off)

**Context:** PR #750 adds AMD Multi-GPU support.

**Decision:** Recommend fast-tracking PR #750 with AMD developer program sign-off.

**Rationale:** This is the single highest-value PR for the AMD partnership. It touches 43 files and 3.9k lines, which is manageable with focused review.

**Consequences:** Requires AMD partnership sign-off. If accepted, PR #750 should be merged before other large PRs.
