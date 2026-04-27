# Executive Summary: DreamServer PR Backlog Triage

**Date:** 2026-04-27
**Auditor:** Automated PR Audit System
**Scope:** 75 open pull requests against Light-Heart-Labs/DreamServer

---

## Headline Numbers

| Verdict | Count | % |
|---------|-------|---|
| **Merge Now** | 59 | 79% |
| **Revise** | 10 | 13% |
| **Reject** | 6 | 8% |

**PRs needing maintainer judgment:** 10 (all "revise" verdicts)

---

## Three Highest-Priority Merges

### 1. PR #988 — Security: Bind llama-server and host agent to loopback
**Why first:** This is a security hardening PR that changes the default bind address from `0.0.0.0` to `127.0.0.1` on Linux. It touches 15 files across the host agent, compose files, and documentation. Given the project's 400+ stars and self-hosted nature, this is the single most important security fix in the backlog.

**AMD impact:** None. The loopback binding applies uniformly across all GPU backends.

### 2. PR #1057 — Host Agent Runtime Hygiene
**Why second:** Seven surgical fixes to `dream-host-agent.py` that address real failure modes: stderr truncation, silent OSError swallowing, HTTP 403/500 conflation, and dict-form Compose volume handling. This is the most impactful single-file PR in the backlog.

**AMD impact:** None. Changes are backend-agnostic.

### 3. PR #1030 — Install Flow Foundation
**Why third:** Restructures the host agent's install flow with proper hook handling, bind-mount anchoring, and post-up state polling. This is a prerequisite for PRs #1057, #1039, #1038, and #1035.

**AMD impact:** None.

---

## Three Highest-Risk Situations

### 1. PR #961 — Mobile Support (Termux/a-Shell)
**Risk:** 12,748 lines, 137 files, first-time contributor (gabsprogrammer). Adds entirely new platform support for Android Termux and iOS a-Shell. **Verdict: Reject (fit)** — out of scope for current roadmap. The project's GPU-dependent architecture makes mobile support fundamentally different from the desktop/server use case.

### 2. PRs #351, #364, #716 — Extensions Library Bloat
**Risk:** Each PR adds 150,000+ lines across 700-800 files. These are competing implementations of extensions library work. **Verdict:** #364 gets revise (needs scope review), #351 and #716 are rejected as superseded. The maintainer needs to decide whether the extensions library should be pruned before any of these land.

### 3. PR #750 — AMD Multi-GPU Support
**Risk:** 3,957 lines, 43 files, from y-coffee-dev (established contributor). This is the single highest-value PR for the AMD developer program partnership. **Verdict: Revise (architectural rework)** — needs AMD partnership sign-off and ROCm compatibility verification.

---

## AMD Partnership Alert

**PRs touching AMD/ROCm paths:**
- **PR #750** (AMD Multi-GPU) — Primary AMD feature. Needs partnership sign-off.
- **PR #1032** (depends_on mirror) — Adds AMD overlay for continue service. Safe to merge.
- **PR #1009** (image-gen default off) — Affects AMD compose overlay. Safe to merge.
- **PR #988** (loopback binding) — Affects all backends including AMD. Safe to merge.

**No PRs regress AMD compatibility.** The AMD overlay files (`compose.amd.yaml`, `compose.gpu-amd.yaml`) are not modified in ways that would break ROCm support.

---

## Dependency Hot Spots

### Host Agent Chain (7 PRs)
```
#988 → #1030 → #1050 → #1057 → #1039 → #1038 → #1035
```
These must be merged in order. Each builds on the previous.

### CLI Chain (12 PRs)
```
#998 → #1002 → #1008 → #1006 → #1007 → #994 → #993 → #999 → #1000 → #997 → #1016 → #1011
```
These must be merged in order. Each enables stricter bash modes or depends on previous changes.

### Extensions Library Cluster (4 PRs)
```
#351, #364, #716, #1027
```
Only #1027 (bind address sweep) is merge-ready. The other three need maintainer judgment on scope.

---

## Cross-PR Patterns

### Pattern 1: yasinBursali Dominance
63 of 75 PRs (84%) are from yasinBursali, the project's primary contributor. These are generally high-quality, well-documented, and follow consistent patterns. The main risk is merge ordering complexity — many PRs are interdependent.

### Pattern 2: Extensions Library Bloat
Three PRs (#351, #364, #716) each add 150,000+ lines to the extensions library. This suggests the library has grown beyond what can be managed through individual PRs. A strategic decision is needed: either prune the library to a core set of services, or accept the bloat and merge the most comprehensive PR (#364).

### Pattern 3: Security Cluster
Four PRs (#988, #994, #1010, #1050) address security/credential handling. These should be prioritized as a group.

### Pattern 4: Apple Silicon Polish
Seven PRs (#1025, #1020, #1016, #1013, #1005, #1004, #999) address Apple Silicon-specific issues. These are all small, focused, and merge-ready.

---

## Recommended Merge Order (First 20)

1. **#988** — Security: loopback binding
2. **#1030** — Install flow foundation
3. **#1050** — Non-POSIX filesystem detection
4. **#1057** — Runtime hygiene
5. **#1039** — Retry logic
6. **#1038** — Hook handling
7. **#1035** — Openclaw recreate
8. **#998** — CLI pipefail
9. **#1002** — CLI set -u
10. **#1008** — CLI pipefail hygiene
11. **#1006** — CLI stderr routing
12. **#1007** — CLI trap quoting
13. **#994** — CLI secret masking
14. **#993** — CLI visual polish
15. **#999** — CLI Apple Silicon
16. **#1000** — CLI json flag
17. **#997** — CLI shell validation
18. **#1016** — CLI Apple GPU polish
19. **#1011** — CLI Bash 3.2
20. **#1010** — Schema secret flags

---

## Strategic Recommendations

1. **Merge the yasinBursali chain first.** 59 PRs are merge-ready, and most are from the primary contributor. This clears 79% of the backlog.

2. **Decide on the extensions library.** Before merging #364 (or any of the large extensions PRs), decide whether to prune the library to a core set of services. The current 33+ services may be too many for maintainability.

3. **Prioritize AMD Multi-GPU (#750).** This is the highest-value PR for the AMD partnership. Schedule a review with AMD's developer program team.

4. **Reject mobile support (#961).** The project's GPU-dependent architecture makes mobile support a fundamentally different product. If mobile is a strategic goal, it should be a separate project.

5. **Establish a PR size policy.** PRs over 1,000 lines should require maintainer pre-approval. The three 150k-line PRs are unmanageable as-is.

---

## Time Estimate

- **Merge-ready PRs (59):** ~2 hours for a maintainer to review and merge in order
- **Revise PRs (10):** ~4 hours for maintainer review + contributor revisions
- **Reject PRs (6):** ~30 minutes to close with explanations
- **Total:** ~6.5 hours to clear the backlog
